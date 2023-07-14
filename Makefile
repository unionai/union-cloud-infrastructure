.PHONY: requirements
requirements:
	pip install -r requirements.txt

.PHONY: lint
lint: requirements
	cfn-lint ./union-ai-admin/aws/*.yaml

.PHONY: generate
generate: requirements
	python union-ai-admin/aws/script/generate.py

.PHONY: black
black: requirements
	black --check union-ai-admin/aws/script/generate.py

.PHONY: create-stack
create-stack: requirements generate lint
	aws cloudformation create-stack \
	  --output text \
	  --stack-name unionai-provisioner-stack \
	  --template-body file://./union-ai-admin/aws/unionai-provisioner-role.template.yaml \
	  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
	aws cloudformation create-stack \
	  --output text \
	  --stack-name unionai-manager-stack \
	  --template-body file://./union-ai-admin/aws/unionai-manager-role.template.yaml \
	  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
	aws cloudformation create-stack \
	  --output text \
	  --stack-name unionai-reader-stack \
	  --template-body file://./union-ai-admin/aws/unionai-reader-role.template.yaml \
	  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
