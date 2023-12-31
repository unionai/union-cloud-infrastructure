> **Warning**
> This set of CloudFormation templates is currently under active development, and frequent changes are being made. Please be aware that the code, features, and documentation might not be fully completed or entirely functional at this stage.

# Union.ai role Stack for AWS

The Union.ai role Stack for AWS gives you a iam role and few policies. Union ai will use these roles for provisioning, management and debugging purpose.

### unionai-provisioner-stack
CloudFormation template allows customers to create an initial provisioner role for provisioning the UnionAI infrastructure. Once the infrastructure is set up, the user can safely delete this role.

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=region#/stacks/new?stackName=unionai-provisioner-stack&templateURL=https://union-public.s3.amazonaws.com/templates/v0.7/unionai-provisioner-role.template.yaml)

#### Resources
- It will create 3 policies:
   - `support-policy`: This policy only provides permissions to list, get, and describe permissions.
   - `updater-policy`: This policy will only provide permissions to modify a few resources, such as node groups, EKS versions, and some EC2 permissions.
   - `provisioner-policy`: This policy only provides full administration permissions, including creating, deleting, tagging, and untagging resources.
- It will create an AWS IAM role `unionai-provisioner-role` and attach all 3 policies to it.

#### AWS CLI Command
To create the stack, use the following AWS CLI command:

```bash
aws cloudformation create-stack \
  --output text \
  --stack-name unionai-provisioner-stack \
  --template-url "https://union-public.s3.amazonaws.com/templates/v0.7/unionai-provisioner-role.template.yaml" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

### unionai-updater-stack
CloudFormation template allows customers to create a updater role for managing the UnionAI infrastructure. The updater role provides permissions to modify specific resources and perform management tasks within the infrastructure.

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=region#/stacks/new?stackName=unionai-provisioner-stack&templateURL=https://union-public.s3.amazonaws.com/templates/v0.7/unionai-updater-role.template.yaml)

#### Resources
- It will create 2 policies:
   - `support-policy`: This policy provides permissions to list, get, and describe resources.
   - `updater-policy`: This policy provides permissions to modify specific resources such as node groups, EKS versions, and certain EC2 permissions.
- It will create an AWS IAM role `unionai-updater-role` and attach all policies to it.

#### AWS CLI Command
To create the stack, use the following AWS CLI command:

```bash
aws cloudformation create-stack \
  --output text \
  --stack-name unionai-updater-stack \
  --template-url "https://union-public.s3.amazonaws.com/templates/v0.7/unionai-updater-role.template.yaml" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

### unionai-support-stack:
CloudFormation template allows customers to create a support role for accessing and viewing resources within the UnionAI infrastructure. The support role provides read-only permissions, allowing users to list, get, and describe resources without the ability to modify or make changes.

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=region#/stacks/new?stackName=unionai-provisioner-stack&templateURL=https://union-public.s3.amazonaws.com/templates/v0.7/unionai-support-role.template.yaml)

#### Resources
- It will create a policy named `support-policy` that provides permissions to list, get, and describe resources.
- It will create an AWS IAM role `unionai-support-role` and attach the `support-policy` to it.

#### AWS CLI Command
To create the stack, use the following AWS CLI command:

```bash
aws cloudformation create-stack \
  --output text \
  --stack-name unionai-support-stack \
  --template-url "https://union-public.s3.amazonaws.com/templates/v0.7/unionai-support-role.template.yaml" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

## Development
To get started with customizing your own stack, or contributing fixes and features:

```bash
# Generate Cloud Formation Stacks
make generate

# Run Lint
make lint

# Create new stack
AWS_PROFILE="some-profile" make create-stack
```

## Release
```bash
# Setup aws credential for unionai
# The make release_cloudformation command will create and push the specified tag in the Git repository. Additionally, it will publish the generated CloudFormation template to the designated S3 bucket.
RELEASE_TAG=v5.1.1 make release_cloudformation
```
