#!/usr/bin/env python3
"""Offline checks for the customer Roles Anywhere CloudFormation template."""

import unittest
from pathlib import Path

import yaml


class Loader(yaml.SafeLoader):
    pass


Loader.add_constructor("!Ref", lambda loader, node: loader.construct_scalar(node))
Loader.add_constructor("!Sub", lambda loader, node: loader.construct_scalar(node))
Loader.add_constructor("!GetAtt", lambda loader, node: loader.construct_scalar(node))
TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "union-ai-admin/aws/union-roles-anywhere.template.yaml"
)
DOCUMENT = yaml.load(TEMPLATE.read_text(), Loader=Loader)
RESOURCES = DOCUMENT["Resources"]


class RolesAnywhereTemplate(unittest.TestCase):
    def test_profiles_have_expected_enablement_and_duration(self):
        deploy = RESOURCES["DeployProfile"]["Properties"]
        break_glass = RESOURCES["BreakGlassProfile"]["Properties"]
        self.assertTrue(deploy["Enabled"])
        self.assertTrue(deploy["AcceptRoleSessionName"])
        self.assertEqual(deploy["DurationSeconds"], 3600)
        self.assertFalse(break_glass["Enabled"])
        self.assertEqual(break_glass["DurationSeconds"], 3600)

    def test_role_trusts_are_limited_to_anchor_and_expected_cn(self):
        for logical_id, cn in (
            ("UnionDeployRole", "union-deploy"),
            ("UnionBreakGlassRole", "union-break-glass"),
        ):
            statement = RESOURCES[logical_id]["Properties"]["AssumeRolePolicyDocument"]["Statement"][0]
            self.assertEqual(statement["Principal"], {"Service": "rolesanywhere.amazonaws.com"})
            self.assertEqual(
                statement["Condition"]["StringEquals"],
                {"aws:SourceArn": "TrustAnchor.Arn", "x509Subject/CN": cn},
            )

    def test_break_glass_has_only_cluster_describe(self):
        policy = RESOURCES["UnionBreakGlassRole"]["Properties"]["Policies"][0]["PolicyDocument"]
        self.assertEqual(policy["Statement"], [{
            "Effect": "Allow",
            "Action": "eks:DescribeCluster",
            "Resource": "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:cluster/*",
        }])


if __name__ == "__main__":
    unittest.main()
