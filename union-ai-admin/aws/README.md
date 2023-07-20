# Union.ai role Stack for AWS

The Union.ai role Stack for AWS gives you a iam role and few policies. Union ai will use these roles for provisioning, management and debugging purpose.

### unionai-provisioner-stack
CloudFormation template allows customers to create an initial provisioner role for provisioning the UnionAI infrastructure. Once the infrastructure is set up, the user can safely delete this role.

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://s3.amazonaws.com/unionai-aws-stack/latest/unionai-provisioner-stack.yml)

#### Resources
- It will create 3 policies:
   - `read-policy`: This policy only provides permissions to list, get, and describe permissions.
   - `manager-policy`: This policy will only provide permissions to modify a few resources, such as node groups, EKS versions, and some EC2 permissions.
   - `provisioner-policy`: This policy only provides full administration permissions, including creating, deleting, tagging, and untagging resources.
- It will create an AWS IAM role `unionai-provisioner-role` and attach all 3 policies to it.

#### AWS CLI Command
To create the stack, use the following AWS CLI command:

```bash
aws cloudformation create-stack \
  --output text \
  --stack-name unionai-provisioner-stack \
  --template-url "https://s3.amazonaws.com/unionai-aws-stack/latest/unionai-provisioner-stack.yml" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

### unionai-manager-stack
CloudFormation template allows customers to create a manager role for managing the UnionAI infrastructure. The manager role provides permissions to modify specific resources and perform management tasks within the infrastructure.

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://s3.amazonaws.com/unionai-aws-stack/latest/unionai-manager-stack.yml)

#### Resources
- It will create 2 policies:
   - `read-policy`: This policy provides permissions to list, get, and describe resources.
   - `manager-policy`: This policy provides permissions to modify specific resources such as node groups, EKS versions, and certain EC2 permissions.
- It will create an AWS IAM role `unionai-manager-role` and attach all policies to it.

#### AWS CLI Command
To create the stack, use the following AWS CLI command:

```bash
aws cloudformation create-stack \
  --output text \
  --stack-name unionai-manager-stack \
  --template-url "https://s3.amazonaws.com/unionai-aws-stack/latest/unionai-manager-stack.yml" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

### unionai-reader-stack:
CloudFormation template allows customers to create a reader role for accessing and viewing resources within the UnionAI infrastructure. The reader role provides read-only permissions, allowing users to list, get, and describe resources without the ability to modify or make changes.

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://s3.amazonaws.com/unionai-aws-stack/latest/unionai-reader-stack.yml)

#### Resources
- It will create a policy named `read-policy` that provides permissions to list, get, and describe resources.
- It will create an AWS IAM role `unionai-reader-role` and attach the `read-policy` to it.

#### AWS CLI Command
To create the stack, use the following AWS CLI command:

```bash
aws cloudformation create-stack \
  --output text \
  --stack-name unionai-reader-stack \
  --template-url "https://s3.amazonaws.com/unionai-aws-stack/latest/unionai-reader-stack.yml" \
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
