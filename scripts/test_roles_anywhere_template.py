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
Loader.add_constructor("!If", lambda loader, node: loader.construct_sequence(node, deep=True))
Loader.add_constructor("!Not", lambda loader, node: loader.construct_sequence(node, deep=True))
Loader.add_constructor("!Equals", lambda loader, node: loader.construct_sequence(node, deep=True))
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
        self.assertEqual(deploy["DurationSeconds"], "DeploySessionDurationSeconds")
        self.assertFalse(break_glass["Enabled"])
        self.assertEqual(break_glass["DurationSeconds"], 3600)

    def test_deploy_session_duration_defaults_to_three_hours(self):
        parameter = DOCUMENT["Parameters"]["DeploySessionDurationSeconds"]
        self.assertEqual(parameter["Default"], 10800)
        self.assertEqual((parameter["MinValue"], parameter["MaxValue"]), (3600, 43200))
        deploy_role = RESOURCES["UnionDeployRole"]["Properties"]
        self.assertEqual(deploy_role["MaxSessionDuration"], "DeploySessionDurationSeconds")
        self.assertNotIn("MaxSessionDuration", RESOURCES["UnionBreakGlassRole"]["Properties"])

    def test_deploy_profile_holds_both_deployment_roles(self):
        self.assertEqual(
            RESOURCES["DeployProfile"]["Properties"]["RoleArns"],
            ["UnionDeployRole.Arn", "UnionCloudDeployerRole.Arn"],
        )
        self.assertEqual(
            RESOURCES["BreakGlassProfile"]["Properties"]["RoleArns"],
            ["UnionBreakGlassRole.Arn"],
        )

    def test_cloud_deployer_trusts_apps_cert_and_reaches_union_clusters_only(self):
        role = RESOURCES["UnionCloudDeployerRole"]["Properties"]
        self.assertEqual(role["MaxSessionDuration"], 3600)
        condition = role["AssumeRolePolicyDocument"]["Statement"][0]["Condition"]["StringEquals"]
        self.assertEqual(condition["aws:PrincipalTag/x509Subject/CN"], "union-deploy-apps")
        statement = role["Policies"][0]["PolicyDocument"]["Statement"]
        self.assertEqual(statement, [{
            "Effect": "Allow",
            "Action": ["eks:DescribeCluster", "eks:AccessKubernetesApi"],
            "Resource": "arn:${AWS::Partition}:eks:${AWS::Region}:${AWS::AccountId}:cluster/opta-*",
        }])

    def test_outputs_cover_customer_handoff(self):
        self.assertEqual(
            set(DOCUMENT["Outputs"]),
            {
                "TrustAnchorArn", "DeployProfileArn", "DeployProfileId",
                "BreakGlassProfileArn", "BreakGlassProfileId",
                "DeployRoleArn", "CloudDeployerRoleArn", "BreakGlassRoleArn",
            },
        )

    def test_role_trusts_are_limited_to_anchor_and_expected_cn(self):
        for logical_id, cn in (
            ("UnionDeployRole", "union-deploy"),
            ("UnionBreakGlassRole", "union-break-glass"),
        ):
            statement = RESOURCES[logical_id]["Properties"]["AssumeRolePolicyDocument"]["Statement"][0]
            self.assertEqual(statement["Principal"], {"Service": "rolesanywhere.amazonaws.com"})
            self.assertEqual(
                statement["Action"],
                ["sts:AssumeRole", "sts:TagSession", "sts:SetSourceIdentity"],
            )
            self.assertEqual(
                statement["Condition"]["StringEquals"],
                {
                    "aws:SourceArn": "TrustAnchor.TrustAnchorArn",
                    "aws:PrincipalTag/x509Subject/CN": cn,
                },
            )

    def test_break_glass_has_only_cluster_describe(self):
        policy = RESOURCES["UnionBreakGlassRole"]["Properties"]["Policies"][0]["PolicyDocument"]
        self.assertEqual(policy["Statement"], [{
            "Effect": "Allow",
            "Action": "eks:DescribeCluster",
            "Resource": "arn:${AWS::Partition}:eks:${AWS::Region}:${AWS::AccountId}:cluster/*",
        }])


if __name__ == "__main__":
    unittest.main()
