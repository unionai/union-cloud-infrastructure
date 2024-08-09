> **Warning**
> This set of CloudFormation templates is currently under active development, and frequent changes are being made. Please be aware that the code, features, and documentation might not be fully completed or entirely functional at this stage.

# Union.ai role Stack for AWS

The Union.ai role Stack for AWS gives you a iam role and few policies. Union ai will use these roles for provisioning, management and debugging purpose.

### unionai-admin-stack
CloudFormation template allows customers to create role for provisioning and managing the UnionAI infrastructure. 

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=region#/stacks/new?stackName=union-ai-admin&templateURL=https://union-public.s3.amazonaws.com/templates/v0.7/union-ai-admin-role.template.yaml)

#### Resources
- It will create an AWS IAM role `union-ai-admin` with 1 inline policy attached.

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
```bash
# Setup aws credential for unionai
# The make release_cloudformation command will create and push the specified tag in the Git repository. Additionally, it will publish the generated CloudFormation template to the designated S3 bucket.
RELEASE_TAG=v5.1.1 make release_cloudformation
```
