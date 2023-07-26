from awacs.aws import (
    Allow,
    PolicyDocument,
    Condition,
    Principal,
    Statement,
    Action,
    StringEqualsIfExists,
)
from awacs.sts import AssumeRole

from troposphere import Ref, Sub, Template
from troposphere.iam import Role, ManagedPolicy, PolicyType

import os

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

# Description for the updater IAM role CloudFormation template
UPDATER_CF_DESCRIPTION = (
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
                    Resource=["arn:aws:s3:::opta-*", "arn:aws:s3:::union-cloud-*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("cloudfront", "GetCloudFrontOriginAccessIdentity"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:cloudfront::${AWS::AccountId}:origin-access-identity/*"
                        )
                    ],
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
                        Action("iam", "GetInstanceProfile"),
                    ],
                    Resource=[
                        Sub("arn:aws:iam::${AWS::AccountId}:oidc-provider/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:instance-profile/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("iam", "GetPolicyVersion"),
                        Action("iam", "GetPolicy"),
                        Action("iam", "GetRole"),
                        Action("iam", "GetRolePolicy"),
                        Action("iam", "ListPolicyVersions"),
                        Action("iam", "ListPolicyTags"),
                        Action("iam", "ListRoleTags"),
                        Action("iam", "ListRoles"),
                        Action("iam", "ListInstanceProfilesForRole"),
                        Action("iam", "ListRolePolicies"),
                        Action("iam", "ListAttachedRolePolicies"),
                    ],
					Resource=[
						Sub("arn:aws:iam::${AWS::AccountId}:policy/opta-*"),
						Sub("arn:aws:iam::${AWS::AccountId}:policy/unionai-*"),
						Sub("arn:aws:iam::${AWS::AccountId}:policy/*userflyterole*"),
						Sub("arn:aws:iam::${AWS::AccountId}:policy/*adminflyterole*"),
						Sub("arn:aws:iam::${AWS::AccountId}:policy/*fluentbitrole*"),
						Sub("arn:aws:iam::${AWS::AccountId}:policy/*fluentbitpolicy*"),
						Sub("arn:aws:iam::${AWS::AccountId}:role/*AWSService*"),
						Sub(
							"arn:aws:iam::${AWS::AccountId}:role/aws-service-role/*.amazonaws.com/*"
						),
						Sub("arn:aws:iam::${AWS::AccountId}:role/opta-*"),
						Sub("arn:aws:iam::${AWS::AccountId}:role/unionai-*"),
						Sub("arn:aws:iam::${AWS::AccountId}:role/*userflyterole*"),
						Sub("arn:aws:iam::${AWS::AccountId}:role/*adminflyterole*"),
						Sub("arn:aws:iam::${AWS::AccountId}:role/*fluentbitrole*"),
					],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("iam", "ListOpenIDConnectProviderTags"),
                        Action("iam", "ListInstanceProfileTags"),
                    ],
                    Resource=[
                        Sub("arn:aws:iam::${AWS::AccountId}:oidc-provider/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:instance-profile/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "DescribeVpcAttribute"),
                    ],
                    Resource=["*"],
                    Condition=Condition(
                        StringEqualsIfExists(
                            "aws:RequestTag/ManagedByUnion",
                            "true",
                        )
                    ),
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


def create_updater_policy(role_type):
    """
    Create a managed policy for the updater IAM role.
    :return: The ManagedPolicy object.
    """
    return ManagedPolicy(
        "UnionaiUpdaterPermission",
        ManagedPolicyName=f"updater-policy-for-{role_type}-role",
        PolicyDocument=PolicyDocument(
            Version="2012-10-17",
            Statement=[
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "ModifyVpcAttribute"),
                        Action("ec2", "ModifyVpcEndpoint"),
                        Action("ec2", "ModifySubnetAttribute"),
                        Action("ec2", "ModifyLaunchTemplate"),
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
                    Condition=Condition(
                        StringEqualsIfExists(
                            "aws:RequestTag/ManagedByUnion",
                            "true",
                        )
                    ),
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
                        Action("autoscaling", "DeleteTags"),
                    ],
                    Resource=["*"],
                    Condition=Condition(
                        StringEqualsIfExists(
                            "aws:RequestTag/ManagedByUnion",
                            "true",
                        )
                    ),
                ),
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
						Sub(
							"arn:aws:eks:${AWS::Region}:${AWS::AccountId}:addon/opta-*/*/*"
						),
                    ],
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
                            "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/eks/opta-*/cluster:log-stream"
                        ),
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
                    Resource=["arn:aws:s3:::opta-*", "arn:aws:s3:::union-cloud-*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("cloudfront", "CreateCloudFrontOriginAccessIdentity"),
                        Action("cloudfront", "DeleteCloudFrontOriginAccessIdentity"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:cloudfront::${AWS::AccountId}:origin-access-identity/*"
                        )
                    ],
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
                        Action("ec2", "AuthorizeSecurityGroupEgress"),
                        Action("ec2", "AuthorizeSecurityGroupIngress"),
                        Action("ec2", "RevokeSecurityGroupIngress"),
                        Action("ec2", "AuthorizeSecurityGroupEgress"),
                        Action("ec2", "CreateSecurityGroup"),
                        Action("ec2", "RevokeSecurityGroupEgress"),
                        Action("ec2", "DeleteSubnet"),
                        Action("ec2", "CreateNatGateway"),
                        Action("ec2", "CreateSubnet"),
                        Action("ec2", "DeleteFlowLogs"),
                        Action("ec2", "CreateFlowLogs"),
                        Action("ec2", "CreateVpc"),
                        Action("ec2", "ReleaseAddress"),
                        Action("ec2", "CreateTags"),
                        Action("ec2", "RunInstances"),
                        Action("ec2", "DeleteTags"),
                        Action("ec2", "CreateLaunchTemplate"),
                        Action("ec2", "CreateLaunchTemplateVersion"),
                        Action("ec2", "CreateVpcEndpoint"),
						Action("ec2", "AssociateAddress"),
						Action("ec2", "DisassociateAddress"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc-endpoint/*"
                        ),
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
                    Condition=Condition(
                        StringEqualsIfExists(
                            "aws:RequestTag/ManagedByUnion",
                            "true",
                        )
                    ),
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "AssociateRouteTable"),
                        Action("ec2", "DeleteSecurityGroup"),
                        Action("ec2", "DeleteVpcEndpoints"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc-endpoint/*"
                        ),
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
                        Action("iam", "CreateInstanceProfile"),
                        Action("iam", "RemoveRoleFromInstanceProfile"),
                        Action("iam", "DeleteInstanceProfile"),
                        Action("iam", "TagInstanceProfile"),
                        Action("iam", "UntagInstanceProfile"),
                        Action("iam", "AddRoleToInstanceProfile"),
                        Action("iam", "UpdateAssumeRolePolicy"),
                    ],
                    Resource=[
                        Sub("arn:aws:iam::${AWS::AccountId}:oidc-provider/*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:instance-profile/*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
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
                    ],
                    Resource=[
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/opta-*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/unionai-*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/*userflyterole*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/*adminflyterole*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/*fluentbitrole*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:policy/*fluentbitpolicy*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/*AWSService*"),
						Sub(
							"arn:aws:iam::${AWS::AccountId}:role/aws-service-role/*.amazonaws.com/*"
						),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/opta-*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/unionai-*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/*userflyterole*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/*adminflyterole*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/*fluentbitrole*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("autoscaling", "CreateLaunchConfiguration"),
                    ],
                    Resource=["*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("autoscaling", "CreateAutoScalingGroup"),
                        Action("autoscaling", "DeleteAutoScalingGroup"),
                        Action("autoscaling", "SetInstanceProtection"),
                    ],
                    Resource=["*"],
                    Condition=Condition(
                        StringEqualsIfExists(
                            "aws:RequestTag/ManagedByUnion",
                            "true",
                        )
                    ),
                ),
            ],
        ),
    )


def create_terraform_policy(role_type):
    """
    Create a managed policy for the admin IAM role used by Terraform.
    :return: The ManagedPolicy object.
    """
    return ManagedPolicy(
        "UnionaiTerraformPermission",
        ManagedPolicyName=f"terraform-policy-for-{role_type}-role",
        PolicyDocument=PolicyDocument(
            Version="2012-10-17",
            Statement=[
                Statement(
                    Effect=Allow,
                    Action=[
						Action("s3", "ListBucket"),
						Action("s3", "GetObject"),
						Action("s3", "PutObject"),
						Action("s3", "DeleteObject"),
                    ],
                    Resource=["arn:aws:s3:::opta-*", "arn:aws:s3:::union-cloud-*"],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("iam", "CreateServiceLinkedRole"),
                        Action("iam", "PassRole"),
                    ],
                    Resource=[
                        Sub(
                            "arn:aws:iam::${AWS::AccountId}:role/aws-service-role/*.amazonaws.com/*"
                        ),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/opta-*"),
                        Sub("arn:aws:iam::${AWS::AccountId}:role/unionai-*"),
                    ],
                ),
                Statement(
                    Effect=Allow,
                    Action=[
                        Action("ec2", "EnableEbsEncryptionByDefault"),
                        Action("ec2", "ModifyEbsDefaultKmsKeyId"),
                        Action("ec2", "DisableEbsEncryptionByDefault"),
                        Action("ec2", "GetEbsEncryptionByDefault"),
                    ],
                    Resource=["*"],
					Condition=Condition(
						StringEqualsIfExists(
							"ec2:Region",
							Sub("${AWS::Region}")
						)
					)
                ),
                Statement(
                    Effect=Allow,
                    Action=[
						Action("dynamodb", "DescribeTable"),
						Action("dynamodb", "GetItem"),
						Action("dynamodb", "PutItem"),
						Action("dynamodb", "DeleteItem"),
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
    for role in ["reader", "updater", "provisioner"]:
        template = Template()
        description = READER_CF_DESCRIPTION
        ref = [Ref(template.add_resource(create_read_policy(role)))]

        if role == "updater":
            description = UPDATER_CF_DESCRIPTION

        if role == "provisioner":
            description = PROVISIONER_CF_DESCRIPTION
            ref.append(Ref(template.add_resource(create_provisioner_policy(role))))

        # This permission is required by Terraform for update/upgrade
        if role == "updater" or role == "provisioner":
            ref.append(Ref(template.add_resource(create_updater_policy(role))))
            ref.append(Ref(template.add_resource(create_terraform_policy(role))))

        template.set_description(description)
        file = f"unionai-{role}"

        template.add_resource(create_role(file, ref))

        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(parent_dir, f"unionai-{role}-role.template.yaml")

        with open(path, "w") as file:
            file.write(template.to_yaml())


if __name__ == "__main__":
    main()
