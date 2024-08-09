export BUCKET_NAME = "union-public"

.PHONY: requirements
requirements:
	pip install -r requirements.txt

.PHONY: cf-lint
cf-lint: requirements
	cfn-lint ./union-ai-admin/aws/gen/*.yaml
	cfn-lint ./union-ai-admin/aws/*.yaml

.PHONY: create-stack
create-stack: requirements cf-lint
	aws cloudformation create-stack \
	  --output text \
	  --stack-name union-ai-admin \
	  --template-body file://./union-ai-admin/aws/union-ai-admin.template.yaml \
	  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

# RELEASE_TAG=v5.1.1 make release_cloudformation
.PHONY: release_cloudformation
release_cloudformation:
	# Create Git Release
	git tag $(RELEASE_TAG)
	git push origin $(RELEASE_TAG)

	# Create directory for the new release
	aws s3api put-object --bucket $(BUCKET_NAME) --key templates/$(RELEASE_TAG)/
	# Upload the CloudFormation template to the new release directory
	aws s3 cp ./union-ai-admin/aws/union-ai-admin-role.template.yaml s3://$(BUCKET_NAME)/templates/$(RELEASE_TAG)/union-ai-admin-role.template.yaml
