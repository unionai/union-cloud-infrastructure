> **Warning**
> This set of CloudFormation templates is currently under active development, and frequent changes are being made. Please be aware that the code, features, and documentation might not be fully completed or entirely functional at this stage.

# Union.ai role Stack for AWS

The Union.ai role Stack for AWS gives you a iam role and few policies. Union ai will use these roles for provisioning, management and debugging purpose.

### unionai-admin-stack
CloudFormation template allows customers to create role for provisioning and managing the UnionAI infrastructure. 

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=region#/stacks/new?stackName=union-ai-admin&templateURL=https://union-public.s3.amazonaws.com/templates/v0.7/union-ai-admin-role.template.yaml)

#### Resources
- It creates an AWS IAM role `union-ai-admin` with one inline policy and a separate
  managed policy for EKS upgrade reads.

#### AWS CLI Command
To create the stack, use the following AWS CLI command:

```bash
aws cloudformation create-stack \
  --output text \
  --stack-name union-ai-admin \
  --template-url "https://union-public.s3.amazonaws.com/templates/v0.7/union-ai-admin-role.template.yaml" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

## Development
To get started with customizing your own stack, or contributing fixes and features:

```bash
# Generate Cloud Formation Stacks
make generate

# Run Lint
make cf-lint

# Create new stack
AWS_PROFILE="some-profile" make create-stack
```

## Release

### EKS upgrade readiness permissions

The template includes regional read access for EKS upgrade insights and update
history, add-on catalogs, EC2 instances and Capacity Reservations, and public EKS
optimized-AMI parameters. EC2 metadata is visible throughout the deployment region;
SSM access does not include customer parameters. Run
`bash scripts/test_eks_upgrade_permissions.sh` for offline scope, policy-size and
CloudFormation checks. The read statements live in `EKSUpgradeReadPolicy`, attached
to the bootstrap role. A separate managed policy keeps the existing inline policy
within the [IAM role policy-size limit](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html).

Merging this template does not update existing customer roles. The companion
`unionai/cloud` module `aws_eks_upgrade_read_permissions` provides an explicit,
per-deployment backfill. Merge both IAM PRs before an EKS rollout; apply that merged
module and verify effective read access before beginning the upgrade. Do not run a
fleet-wide role update. Keep the four `ReadEKSUpgrade*` / `ReadEKSOptimizedAMIs`
statements identical in the two repos, including region conditions. Existing grants
are preserved, including the redundant resource-scoped add-on catalog entry.

The release command below publishes the template and writes Git history. It is a
separate operator action; tests and the customer backfill do not require running it.

```bash
# Setup aws credential for unionai
# The make release_cloudformation command will create and push the specified tag in the Git repository. Additionally, it will publish the generated CloudFormation template to the designated S3 bucket.
RELEASE_TAG=v5.1.1 make release_cloudformation
```
