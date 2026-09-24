#!/usr/bin/env python3
"""Offline scope checks for the shared EKS upgrade read permissions."""

import fnmatch
import json
import unittest
from pathlib import Path

import yaml


class Loader(yaml.SafeLoader):
    pass


Loader.add_constructor("!Ref", lambda loader, node: loader.construct_scalar(node))
Loader.add_constructor("!Sub", lambda loader, node: loader.construct_scalar(node))
Loader.add_constructor("!GetAtt", lambda loader, node: loader.construct_sequence(node))
TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "union-ai-admin/aws/union-ai-admin-role.template.yaml"
)
DOCUMENT = yaml.load(TEMPLATE.read_text(), Loader=Loader)
POLICY = DOCUMENT["Resources"]["EKSUpgradeReadPolicy"]["Properties"]["PolicyDocument"]
STATEMENTS = {
    s["Sid"]: s
    for s in POLICY["Statement"]
    if s.get("Sid", "").startswith(("ReadEKSUpgrade", "ReadEKSOptimized"))
}


class UpgradePermissions(unittest.TestCase):
    def test_managed_policy_attaches_to_the_bootstrap_role(self):
        resource = DOCUMENT["Resources"]["EKSUpgradeReadPolicy"]
        self.assertEqual(resource["Type"], "AWS::IAM::ManagedPolicy")
        self.assertEqual(
            resource["Properties"]["Roles"],
            ["CrossAccountRoleForAWSTrustedAdvisorUnion"],
        )

    def test_policy_sizes_fit_aws_limits_including_long_region_names(self):
        inline_size = 0
        for resource in DOCUMENT["Resources"].values():
            if resource["Type"] not in ("AWS::IAM::Policy", "AWS::IAM::ManagedPolicy"):
                continue
            document = resource["Properties"]["PolicyDocument"]
            rendered = (
                json.dumps(document, separators=(",", ":"), default=str)
                .replace("${AWS::Region}", "ap-southeast-7")
                .replace("${AWS::AccountId}", "123456789012")
            )
            if resource["Type"] == "AWS::IAM::Policy":
                inline_size += len(rendered)
            else:
                self.assertLessEqual(len(rendered), 6144)
        self.assertLessEqual(inline_size, 10240)

    def test_only_seven_read_actions(self):
        self.assertEqual(len(STATEMENTS), 4)
        self.assertEqual(
            {a for s in STATEMENTS.values() for a in s["Action"]},
            {
                "eks:ListInsights",
                "eks:DescribeInsight",
                "eks:ListUpdates",
                "eks:DescribeAddonVersions",
                "ec2:DescribeInstances",
                "ec2:DescribeCapacityReservations",
                "ssm:GetParameters",
            },
        )
        self.assertTrue(all(s["Effect"] == "Allow" for s in STATEMENTS.values()))

    def test_insights_and_updates_stay_in_deployment(self):
        resources = STATEMENTS["ReadEKSUpgradeInsights"]["Resource"]
        self.assertEqual(
            set(resources),
            {
                "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:cluster/opta-*",
                "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:cluster/union-*",
            },
        )
        updates = STATEMENTS["ReadEKSUpgradeUpdates"]["Resource"]
        self.assertEqual(
            set(updates),
            {
                r.replace(":cluster/", f":{kind}/")
                for r in resources
                for kind in ("cluster", "nodegroup", "addon")
            },
        )

    def test_catalog_and_capacity_are_region_limited(self):
        statement = STATEMENTS["ReadEKSUpgradeCatalogAndCapacity"]
        self.assertEqual(statement["Resource"], "*")
        self.assertEqual(
            statement["Condition"],
            {"StringEquals": {"aws:RequestedRegion": "AWS::Region"}},
        )

    def test_ssm_cannot_read_customer_parameters(self):
        resources = STATEMENTS["ReadEKSOptimizedAMIs"]["Resource"]
        self.assertEqual(
            resources,
            ["arn:aws:ssm:${AWS::Region}::parameter/aws/service/eks/optimized-ami/*"],
        )
        patterns = [r.replace("${AWS::Region}", "us-east-1") for r in resources]
        self.assertFalse(
            any(
                fnmatch.fnmatchcase(
                    "arn:aws:ssm:us-east-1:587590817183:parameter/customer/secret", p
                )
                for p in patterns
            )
        )


if __name__ == "__main__":
    unittest.main()
