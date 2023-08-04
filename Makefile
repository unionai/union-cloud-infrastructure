export BUCKET_NAME = "union-public"

.PHONY: requirements
requirements:
	pip install -r requirements.txt

.PHONY: cf-lint
cf-lint: requirements
	cfn-lint ./union-ai-admin/aws/gen/*.yaml
	cfn-lint ./union-ai-admin/aws/*.yaml

.PHONY: generate
generate:
	python union-ai-admin/aws/script/generate.py

.PHONY: lint
lint: requirements
	black --check union-ai-admin/aws/script/generate.py

.PHONY: create-stack
create-stack: requirements lint generate cf-lint
	aws cloudformation create-stack \
	  --output text \
	  --stack-name unionai-provisioner-stack \
	  --template-body file://./union-ai-admin/aws/unionai-provisioner-role.template.yaml \
	  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
	aws cloudformation create-stack \
	  --output text \
	  --stack-name unionai-updater-stack \
	  --template-body file://./union-ai-admin/aws/unionai-updater-role.template.yaml \
	  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
	aws cloudformation create-stack \
	  --output text \
	  --stack-name unionai-support-stack \
	  --template-body file://./union-ai-admin/aws/unionai-support-role.template.yaml \
	  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

# BUCKET_NAME=union-public,RELEASE_TAG=v5.1.1 make release_cloudformation
.PHONY: release_cloudformation
release_cloudformation:
	# Create Git Release
	git tag $(RELEASE_TAG)
	git push origin $(RELEASE_TAG)

	# Create directory for the new release
	aws s3api put-object --bucket $(BUCKET_NAME) --key templates/$(RELEASE_TAG)/
	# Upload the CloudFormation template to the new release directory
	aws s3 cp ./union-ai-admin/aws/gen/unionai-provisioner-role.template.yaml s3://$(BUCKET_NAME)/templates/$(RELEASE_TAG)/unionai-provisioner-role.template.yaml
	aws s3 cp ./union-ai-admin/aws/gen/unionai-updater-role.template.yaml s3://$(BUCKET_NAME)/templates/$(RELEASE_TAG)/unionai-updater-role.template.yaml
	aws s3 cp ./union-ai-admin/aws/gen/unionai-support-role.template.yaml s3://$(BUCKET_NAME)/templates/$(RELEASE_TAG)/unionai-support-role.template.yaml
	aws s3 cp ./union-ai-admin/aws/union-ai-admin-role.template.yaml s3://$(BUCKET_NAME)/templates/$(RELEASE_TAG)/union-ai-admin-role.template.yaml
