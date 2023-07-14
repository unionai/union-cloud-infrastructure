# Union.ai role Stack for AWS

The Union.ai role Stack for AWS gives you a iam role and few policies. Union ai will use these roles for provisioning, management and debugging purpose.

## Getting started

jump straight in:

TDOD: Button

or If you want to use the [AWS CLI](https://aws.amazon.com/cli/)  then run the below command:

- `unionai-provisioner-stack`: This template allows the customer to create an provisioner role initially for provisioning the UnionAI infrastructure. Once the infrastructure is set up, the user can safely delete this role.
```bash
aws cloudformation create-stack \
  --output text \
  --stack-name unionai-provisioner-stack \
  --template-url "https://s3.amazonaws.com/unionai-aws-stack/latest/unionai-provisioner-stack.yml" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

- `unionai-manager-stack`: This template enables the customer to create a role for management purposes, without granting create/delete/tag/untag permissions.
```bash
aws cloudformation create-stack \
  --output text \
  --stack-name unionai-manager-stack \
  --template-url "https://s3.amazonaws.com/unionai-aws-stack/latest/unionai-manager-stack.yml" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

- `unionai-reader-stack`: This template enables the customer to create a role for debug purposes.

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
