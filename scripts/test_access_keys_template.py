#!/usr/bin/env python3
"""Offline checks for the customer access-key CloudFormation template."""

import unittest
from pathlib import Path

import yaml


class Loader(yaml.SafeLoader):
    pass


for tag in ("!Ref", "!Sub", "!GetAtt"):
    Loader.add_constructor(tag, lambda loader, node: loader.construct_scalar(node)
                           if isinstance(node, yaml.ScalarNode)
                           else loader.construct_sequence(node, deep=True))
for tag in ("!If", "!Not", "!Equals", "!Join"):
    Loader.add_constructor(tag, lambda loader, node: loader.construct_sequence(node, deep=True))

TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "union-ai-admin/aws/union-access-keys.template.yaml"
)
DOCUMENT = yaml.load(TEMPLATE.read_text(), Loader=Loader)
RESOURCES = DOCUMENT["Resources"]
STS_ACTIONS = ["sts:AssumeRole", "sts:TagSession", "sts:SetSourceIdentity"]


def trust(logical_id):
    return RESOURCES[logical_id]["Properties"]["AssumeRolePolicyDocument"]["Statement"]


def user_statements(logical_id):
    return RESOURCES[logical_id]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]


class AccessKeysTemplate(unittest.TestCase):
    def test_no_roles_anywhere_resources(self):
        types = {resource["Type"] for resource in RESOURCES.values()}
        self.assertFalse(any(t.startswith("AWS::RolesAnywhere::") for t in types))

    def test_deploy_roles_trust_only_the_access_user(self):
        for logical_id in ("UnionDeployRole", "UnionCloudDeployerRole"):
            statements = trust(logical_id)
            self.assertEqual(len(statements), 1)
            self.assertEqual(statements[0]["Principal"], {"AWS": "UnionAccessUser.Arn"})
            self.assertEqual(statements[0]["Action"], STS_ACTIONS)

    def test_deploy_role_requires_run_session_name(self):
        condition = trust("UnionDeployRole")[0]["Condition"]
        self.assertEqual(condition, {"StringLike": {"sts:RoleSessionName": "union-deploy-*"}})

    def test_break_glass_role_trusts_only_the_break_glass_user(self):
        statement = trust("UnionBreakGlassRole")[0]
        self.assertEqual(statement["Principal"], {"AWS": "UnionBreakGlassUser.Arn"})
        self.assertEqual(
            statement["Condition"],
            {"StringLike": {"sts:RoleSessionName": "union-break-glass-*"}},
        )
        policy = RESOURCES["UnionBreakGlassRole"]["Properties"]["Policies"][0]["PolicyDocument"]
        self.assertEqual(policy["Statement"], [{
            "Effect": "Allow",
            "Action": "eks:DescribeCluster",
            "Resource": "arn:${AWS::Partition}:eks:${AWS::Region}:${AWS::AccountId}:cluster/*",
        }])

    def test_users_can_only_assume_their_roles(self):
        access = user_statements("UnionAccessUser")[0]
        self.assertEqual(access["Effect"], "Allow")
        self.assertEqual(access["Action"], STS_ACTIONS)
        self.assertEqual(access["Resource"], [
            "arn:${AWS::Partition}:iam::${AWS::AccountId}:role/${RoleDeployName}",
            "arn:${AWS::Partition}:iam::${AWS::AccountId}:role/${RoleCloudDeployerName}",
        ])
        break_glass = user_statements("UnionBreakGlassUser")[0]
        self.assertEqual(
            break_glass["Resource"],
            "arn:${AWS::Partition}:iam::${AWS::AccountId}:role/${RoleBreakGlassName}",
        )

    def test_source_ip_deny_is_conditional_on_both_users(self):
        for logical_id in ("UnionAccessUser", "UnionBreakGlassUser"):
            condition, deny, otherwise = user_statements(logical_id)[1]
            self.assertEqual(condition, "RestrictSourceIp")
            self.assertEqual(deny["Effect"], "Deny")
            self.assertEqual(deny["Condition"], {"NotIpAddress": {"aws:SourceIp": "AllowedSourceCidrs"}})
            self.assertEqual(otherwise, "AWS::NoValue")

    def test_access_key_and_secret_only_when_requested(self):
        self.assertEqual(DOCUMENT["Parameters"]["CreateAccessKeyInStack"]["Default"], "false")
        self.assertEqual(RESOURCES["UnionAccessKey"]["Condition"], "KeyInStack")
        self.assertEqual(RESOURCES["UnionAccessKeySecret"]["Condition"], "KeyInStack")
        self.assertEqual(RESOURCES["UnionAccessKey"]["Properties"]["UserName"], "UnionAccessUser")
        self.assertNotIn("AWS::IAM::AccessKey", {
            RESOURCES[r]["Type"] for r in RESOURCES if r != "UnionAccessKey"
        })

    def test_secret_value_never_in_outputs(self):
        for name, output in DOCUMENT["Outputs"].items():
            self.assertNotIn("SecretAccessKey", str(output["Value"]), name)
        self.assertEqual(DOCUMENT["Outputs"]["AccessKeySecretArn"]["Condition"], "KeyInStack")

    def test_session_durations(self):
        parameter = DOCUMENT["Parameters"]["DeploySessionDurationSeconds"]
        self.assertEqual(parameter["Default"], 10800)
        self.assertEqual(
            RESOURCES["UnionDeployRole"]["Properties"]["MaxSessionDuration"],
            "DeploySessionDurationSeconds",
        )
        self.assertEqual(RESOURCES["UnionCloudDeployerRole"]["Properties"]["MaxSessionDuration"], 3600)

    def test_deploy_policy_grants_no_user_or_key_actions(self):
        text = TEMPLATE.read_text()
        policy_section = text[text.index("  EKSUpgradeReadPolicy:"):text.index("Outputs:")]
        for action in ("iam:CreateUser", "iam:CreateAccessKey", "iam:UpdateAccessKey", "iam:*"):
            self.assertNotIn(action, policy_section)


if __name__ == "__main__":
    unittest.main()
