from awacs.aws import (
    Allow,
    PolicyDocument,
    Principal,
    Statement,
    Action,
)
from awacs.sts import AssumeRole

from troposphere import Ref, Sub, Template
from troposphere.iam import Role, ManagedPolicy, PolicyType

import yaml
import os
import string
import random

# Description for the reader IAM role CloudFormation template
READER_CF_DESCRIPTION = (
    "UnionAI Reader CloudFormation Template: "
    "This CloudFormation template is used to create a reader IAM role for UnionAI. The role's "
    "primary purpose is "
    "to grant read-only access to UnionAI resources. By using this role, users will have the "
    "ability to view and "
    "retrieve information from UnionAI resources while maintaining strict restrictions on "
    "modifying or altering them. "
)

# Description for the manager IAM role CloudFormation template
MANAGER_CF_DESCRIPTION = (
    "UnionAI Management CloudFormation Template: "
    "This CloudFormation template is responsible for creating a management IAM role that UnionAI "
    "will utilize. "
    "This role is intended for management purposes and does not grant permissions for creating, "
    "deleting, tagging, "
    "or untagging resources. Its purpose is to provide necessary access for efficiently managing "
    "UnionAI resources."
)

# Description for the provisioner IAM role CloudFormation template
PROVISIONER_CF_DESCRIPTION = (
    "UnionAI Provisioner CloudFormation Template: "
    "This CloudFormation template is designed to create an admin IAM role specifically for "
    "UnionAI to trust. The "
    "purpose of this role is to enable UnionAI to provision the infrastructure required for "
    "its operations."
)


def create_read_policy(role_type):
    """
    Create a managed policy for the reader IAM role.
    :return: The ManagedPolicy object.
    """
    return ManagedPolicy(
        "UnionaiReaderPermission",
        ManagedPolicyName=f"reader-policy-for-{role_type}-role",
        PolicyDocument=PolicyDocument(
            Version="2012-10-17",
            Statement=[
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("logs", "DescribeLogGroups"),
                        Action("logs", "DescribeDBSubnetGroups"),
                        Action("logs", "DescribeLogStreams"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:opta-*"
                        ),
                        Sub(
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group::log-stream*"
                        ),
                        Sub(
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/eks/opta-*:*"
                        ),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("logs", "ListTagsLogGroup"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:opta-*"
                        ),
                        Sub(
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group::log-stream*"
                        ),
                        Sub(
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/eks/opta-*:*"
                        ),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("s3", "GetBucketLogging"),
                        Action("s3", "GetAccelerateConfiguration"),
                        Action("s3", "GetBucketAcl"),
                        Action("s3", "GetBucketCORS"),
                    ],
                    Resource=["arn:aws:s3:::opta-*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("autoscaling", "DescribeAutoScalingGroups"),
                        Action("autoscaling", "DescribeScalingActivities"),
                        Action("autoscaling", "DescribeTags"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("eks", "DescribeCluster"),
                        Action("eks", "DescribeNodegroup"),
                        Action("eks", "DescribeUpdate"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:cluster/opta-*"
                        ),
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:nodegroup/opta-*/opta-*/*"
                        ),
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:nodegroup/opta-*"
                        ),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("eks", "ListTagsForResource"),
                        Action("eks", "ListNodegroups"),
                        Action("eks", "ListTagsForResource"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:cluster/opta-*"
                        ),
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:nodegroup/opta-*/opta-*/*"
                        ),
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:nodegroup/opta-*"
                        ),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("kms", "GetKeyPolicy"),
                        Action("kms", "GetKeyRotationStatus"),
                        Action("kms", "DescribeKey"),
                    ],
                    Resource=[
                        Sub("arn:aws:kms:${AWS::Region}:${AWS::AccountId}:alias/*"),
                        Sub("arn:aws:kms:${AWS::Region}:${AWS::AccountId}:key/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("kms", "ListResourceTags"),
                        Action("kms", "ListAliases"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("iam", "GetOpenIDConnectProvider"),
                        Action("iam", "GetPolicyVersion"),
                        Action("iam", "GetPolicy"),
                        Action("iam", "GetRole"),
                        Action("iam", "GetRolePolicy"),
                        Action("iam", "GetInstanceProfile"),
                    ],
                    Resource=[
                        Sub("arn:aws:iam::${AWS::AccountId}:oidc-provider/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:instance-profile/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("iam", "ListOpenIDConnectProviderTags"),
                        Action("iam", "ListPolicyVersions"),
                        Action("iam", "ListPolicyTags"),
                        Action("iam", "ListRoleTags"),
                        Action("iam", "ListInstanceProfilesForRole"),
                        Action("iam", "ListInstanceProfileTags"),
                        Action("iam", "ListRoles"),
                        Action("iam", "ListRolePolicies"),
                        Action("iam", "ListAttachedRolePolicies"),
                    ],
                    Resource=[
                        Sub("arn:aws:iam::${AWS::AccountId}:oidc-provider/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:instance-profile/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "DescribeAccountAttributes"),
                        Action("ec2", "DescribeAddresses"),
                        Action("ec2", "DescribeAvailabilityZones"),
                        Action("ec2", "DescribeFlowLogs"),
                        Action("ec2", "DescribeInstanceTypeOfferings"),
                        Action("ec2", "DescribeInternetGateways"),
                        Action("ec2", "DescribeNatGateways"),
                        Action("ec2", "DescribeNetworkAcls"),
                        Action("ec2", "AssociateAddress"),
                        Action("ec2", "DisassociateAddress"),
                        Action("ec2", "DescribeNetworkInterfaces"),
                        Action("ec2", "DescribePrefixLists"),
                        Action("ec2", "DescribeRouteTables"),
                        Action("ec2", "DescribeSecurityGroupRules"),
                        Action("ec2", "DescribeSecurityGroups"),
                        Action("ec2", "DescribeSubnets"),
                        Action("ec2", "DescribeVpcAttribute"),
                        Action("ec2", "DescribeVpcClassicLink"),
                        Action("ec2", "DescribeVpcClassicLinkDnsSupport"),
                        Action("ec2", "DescribeVpcEndpoints"),
                        Action("ec2", "DescribeVpcs"),
                        Action("ec2", "DescribeImages"),
                        Action("ec2", "DescribeLaunchTemplates"),
                        Action("ec2", "DescribeLaunchTemplateVersions"),
                        Action("ec2", "GetEbsEncryptionByDefault"),
                    ],
                    Resource=["*"],
                ),
            ],
        ),
    )


def create_manager_policy(role_type):
    """
    Create a managed policy for the manager IAM role.
    :return: The ManagedPolicy object.
    """
    return ManagedPolicy(
        "UnionaiManagerPermission",
        ManagedPolicyName=f"manager-policy-for-{role_type}-role",
        PolicyDocument=PolicyDocument(
            Version="2012-10-17",
            Statement=[
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "ModifySubnetAttribute"),
                        Action("ec2", "ModifyVpcAttribute"),
                        Action("ec2", "ModifyEbsDefaultKmsKeyId"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:internet-gateway/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:elastic-ip/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:natgateway/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:route-table/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:subnet/subnet-*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:security-group-rule/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:security-group/*"
                        ),
                        Sub("arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:subnet/*"),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc-flow-log/*"
                        ),
                        Sub("arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "ModifyVpcEndpoint"),
                    ],
                    Resource=[
                        Sub("arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc/vpc*"),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc/vpc-endpoint/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:route-table/*"
                        ),
                        Sub("arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:subnet/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "ModifyLaunchTemplate"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("eks", "UpdateNodegroupConfig"),
                        Action("eks", "UpdateNodegroupVersion"),
                        Action("eks", "UpdateClusterConfig"),
                        Action("eks", "UpdateClusterVersion"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:cluster/opta-*"
                        ),
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:nodegroup/opta-*/opta-*/*"
                        ),
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:nodegroup/opta-*"
                        ),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("autoscaling", "UpdateAutoScalingGroup"),
                        Action("autoscaling", "CreateOrUpdateTags"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("eks", "CreateAddon"),
                        Action("eks", "UpdateAddon"),
                        Action("eks", "DeleteAddon"),
                        Action("eks", "DescribeAddonVersions"),
                        Action("eks", "DescribeAddon"),
                        Action("eks", "ListAddons"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:cluster/opta-*"
                        ),
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:addon/opta-*/*/*"
                        ),
                    ],
                ),
            ],
        ),
    )


def create_provisioner_policy(role_type):
    """
    Create a managed policy for the provisioner IAM role.
    :return: The ManagedPolicy object.
    """
    return ManagedPolicy(
        "UnionaiProvisionerPermission",
        ManagedPolicyName=f"provisioner-policy-for-{role_type}-role",
        PolicyDocument=PolicyDocument(
            Version="2012-10-17",
            Statement=[
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("logs", "TagLogGroup"),
                        Action("logs", "DeleteLogGroup"),
                        Action("logs", "CreateLogGroup"),
                        Action("logs", "PutRetentionPolicy"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:opta-*"
                        ),
                        Sub(
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group::log-stream*"
                        ),
                        Sub(
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/eks/opta-*:*"
                        ),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("s3", "CreateBucket"),
                        Action("s3", "DeleteBucketPolicy"),
                        Action("s3", "DeleteBucket"),
                        Action("s3", "*"),
                    ],
                    Resource=["arn:aws:s3:::opta-*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "AllocateAddress"),
                        Action("ec2", "AttachInternetGateway"),
                        Action("ec2", "DetachInternetGateway"),
                        Action("ec2", "CreateInternetGateway"),
                        Action("ec2", "DeleteInternetGateway"),
                        Action("ec2", "CreateNatGateway"),
                        Action("ec2", "DeleteNatGateway"),
                        Action("ec2", "CreateRoute"),
                        Action("ec2", "DeleteRoute"),
                        Action("ec2", "CreateRouteTable"),
                        Action("ec2", "DeleteRouteTable"),
                        Action("ec2", "DisassociateRouteTable"),
                        Action("ec2", "AssociateRouteTable"),
                        Action("ec2", "AuthorizeSecurityGroupEgress"),
                        Action("ec2", "AuthorizeSecurityGroupIngress"),
                        Action("ec2", "RevokeSecurityGroupIngress"),
                        Action("ec2", "AuthorizeSecurityGroupEgress"),
                        Action("ec2", "CreateSecurityGroup"),
                        Action("ec2", "RevokeSecurityGroupEgress"),
                        Action("ec2", "DeleteSecurityGroup"),
                        Action("ec2", "DeleteSubnet"),
                        Action("ec2", "CreateNatGateway"),
                        Action("ec2", "CreateSubnet"),
                        Action("ec2", "CreateNatGateway"),
                        Action("ec2", "DeleteFlowLogs"),
                        Action("ec2", "CreateFlowLogs"),
                        Action("ec2", "DeleteSubnet"),
                        Action("ec2", "CreateVpc"),
                        Action("ec2", "AttachInternetGateway"),
                        Action("ec2", "DetachInternetGateway"),
                        Action("ec2", "DeleteVpc"),
                        Action("ec2", "CreateSubnet"),
                        Action("ec2", "ReleaseAddress"),
                        Action("ec2", "CreateTags"),
                        Action("ec2", "EnableEbsEncryptionByDefault"),
                        Action("ec2", "DisableEbsEncryptionByDefault"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:internet-gateway/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:elastic-ip/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:natgateway/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:route-table/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:subnet/subnet-*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:security-group-rule/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:security-group/*"
                        ),
                        Sub("arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:subnet/*"),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc-flow-log/*"
                        ),
                        Sub("arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "RunInstances"),
                        Action("ec2", "DeleteTags"),
                        Action("ec2", "CreateLaunchTemplate"),
                        Action("ec2", "CreateLaunchTemplateVersion"),
                        Action("ec2", "DeleteLaunchTemplate"),
                        Action("ec2", "DeleteLaunchTemplateVersions"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("eks", "DeleteCluster"),
                        Action("eks", "CreateCluster"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:cluster/opta-*"
                        ),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("kms", "CreateAlias"),
                        Action("kms", "DeleteAlias"),
                        Action("kms", "EnableKeyRotation"),
                        Action("kms", "PutKeyPolicy"),
                        Action("kms", "ScheduleKeyDeletion"),
                        Action("kms", "TagResource"),
                        Action("kms", "UntagResource"),
                        Action("kms", "CreateGrant"),
                    ],
                    Resource=[
                        Sub("arn:aws:kms:${AWS::Region}:${AWS::AccountId}:alias/*"),
                        Sub("arn:aws:kms:${AWS::Region}:${AWS::AccountId}:key/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("kms", "CreateKey"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("iam", "DeleteOpenIDConnectProvider"),
                        Action("iam", "CreateOpenIDConnectProvider"),
                        Action("iam", "TagOpenIDConnectProvider"),
                        Action("iam", "UntagOpenIDConnectProvider"),
                        Action("iam", "CreatePolicy"),
                        Action("iam", "DeletePolicy"),
                        Action("iam", "TagPolicy"),
                        Action("iam", "UntagPolicy"),
                        Action("iam", "TagRole"),
                        Action("iam", "UntagRole"),
                        Action("iam", "CreateRole"),
                        Action("iam", "DeleteRole"),
                        Action("iam", "AttachRolePolicy"),
                        Action("iam", "PutRolePolicy"),
                        Action("iam", "DetachRolePolicy"),
                        Action("iam", "DeleteRolePolicy"),
                        Action("iam", "CreateInstanceProfile"),
                        Action("iam", "RemoveRoleFromInstanceProfile"),
                        Action("iam", "DeleteInstanceProfile"),
                        Action("iam", "TagInstanceProfile"),
                        Action("iam", "UntagInstanceProfile"),
                    ],
                    Resource=[
                        Sub("arn:aws:iam::${AWS::AccountId}:oidc-provider/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:instance-profile/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("autoscaling", "CreateAutoScalingGroup"),
                        Action("autoscaling", "DeleteAutoScalingGroup"),
                        Action("autoscaling", "CreateLaunchConfiguration"),
                        Action("autoscaling", "SetInstanceProtection"),
                        Action("autoscaling", "DeleteTags"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "CreateVpcEndpoint"),
                        Action("ec2", "DeleteVpcEndpoints"),
                        Action("ec2", "CreateTags"),
                    ],
                    Resource=[
                        Sub("arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc/vpc*"),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc-endpoint/*"
                        ),
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:route-table/*"
                        ),
                        Sub("arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:subnet/*"),
                    ],
                ),
            ],
        ),
    )


def create_admin_policy(role_type):
    """
    Create a managed policy for the admin IAM role used by Terraform.
    :return: The ManagedPolicy object.
    """
    return ManagedPolicy(
        "UnionaiAdminPermission",
        ManagedPolicyName=f"admin-policy-for-{role_type}-role",
        PolicyDocument=PolicyDocument(
            Version="2012-10-17",
            Statement=[
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("eks", "CreateNodegroup"),
                        Action("eks", "TagResource"),
                        Action("eks", "UntagResource"),
                        Action("eks", "DeleteNodegroup"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:cluster/opta-*"
                        ),
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:nodegroup/opta-*/opta-*/*"
                        ),
                        Sub(
                            "arn:aws:eks:${AWS::Region}:${AWS::AccountId}:nodegroup/opta-*"
                        ),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("s3", "*"),
                    ],
                    Resource=["arn:aws:s3:::opta-*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("iam", "CreateServiceLinkedRole"),
                        Action("iam", "PassRole"),
                    ],
                    Resource=[
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("autoscaling", "CreateOrUpdateTags"),
                        Action("autoscaling", "DeleteTags"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "EnableEbsEncryptionByDefault"),
                        Action("ec2", "GetEbsEncryptionByDefault"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("dynamodb", "*"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/opta-*"
                        )
                    ],
                ),
            ],
        ),
    )


def create_role(name, policy_arn):
    """
    Create a managed policy for the IAM role.
    :param name: The name of the IAM role.
    :param policy_arn: The list of policy ARNs.
    :return: The Role object.
    """
    return Role(
        "CrossAccountRoleForAWSTrustedAdvisorUnion",
        RoleName=name,
        AssumeRolePolicyDocument=PolicyDocument(
            Version="2012-10-17",
            Statement=[
                Statement(
                    Effect=Allow,
                    Action=[AssumeRole],
                    Principal=Principal("AWS", "arn:aws:iam::479331373192:root"),
                )
            ],
        ),
        ManagedPolicyArns=policy_arn,
    )


def main():
    for role in ["reader", "manager", "provisioner"]:
        template = Template()
        description = READER_CF_DESCRIPTION
        ref = [Ref(template.add_resource(create_read_policy(role)))]

        if role == "manager":
            description = MANAGER_CF_DESCRIPTION

        if role == "provisioner":
            ref.append(Ref(template.add_resource(create_provisioner_policy(role))))
            description = PROVISIONER_CF_DESCRIPTION

        # This permission is required by Terraform for update/upgrade
        if role == "manager" or role == "provisioner":
            ref.append(Ref(template.add_resource(create_manager_policy(role))))
            ref.append(Ref(template.add_resource(create_admin_policy(role))))

        template.set_description(description)
        template.add_resource(create_role(f"unionai-{role}-role", ref))

        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(parent_dir, f"unionai-{role}-role.template.yaml")

        with open(path, "w") as file:
            file.write(template.to_yaml())


if __name__ == "__main__":
    main()
