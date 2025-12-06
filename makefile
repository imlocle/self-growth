.PHONY: deploy clean zip-all zip-layer $(LAMBDAS:%=zip-%) generate-backend-config terraform-init terraform-apply

#####################################
# Config
#####################################

ENV ?= dev
PROJECT_NAME = self-growth
REGION = us-west-1

BUILD_DIR = terraform/builds
LAYER_ZIP = $(BUILD_DIR)/python.zip

# List all Lambda logical names (WITHOUT env suffix or .zip)
LAMBDAS = create-todo get-todo get-all-todo update-todo

BACKEND_CONFIG_TMP = terraform/backend.auto.hcl

PYTHON_LAYER_IMAGE = public.ecr.aws/sam/build-python3.13

#####################################
# Clean
#####################################

clean:
	rm -f $(BUILD_DIR)/*.zip $(BACKEND_CONFIG_TMP)
	rm -rf lambda_layer/python

#####################################
# Ensure build directory exists
#####################################

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

#####################################
# Lambda Layer
#####################################

zip-layer: $(BUILD_DIR)
	rm -rf lambda_layer/python
	mkdir -p lambda_layer/python
	docker run --rm \
		--platform linux/amd64 \
		-v $(CURDIR)/src:/var/task \
		-v $(CURDIR)/lambda_layer/python:/lambda/python \
		$(PYTHON_LAYER_IMAGE) \
		/bin/sh -c "pip3 install -r /var/task/requirements.txt -t /lambda/python --no-cache-dir"
	cd lambda_layer && zip -r ../$(LAYER_ZIP) python > /dev/null

#####################################
# Zip each Lambda (pattern rule)
#####################################

# Usage:
#   make zip-create-todo
#   make zip-get-todo
#   ...
zip-%: $(BUILD_DIR)
	cd src && zip -r ../$(BUILD_DIR)/${PROJECT_NAME}-$*-$(ENV).zip . > /dev/null

#####################################
# Zip all code (layer + lambdas)
#####################################

zip-all: zip-layer $(LAMBDAS:%=zip-%)

#####################################
# Backend config
#####################################

generate-backend-config:
	@echo "bucket = \"$(PROJECT_NAME)-terraform-state-bucket\"" > $(BACKEND_CONFIG_TMP)
	@echo "key    = \"$(PROJECT_NAME)/$(ENV)/terraform.tfstate\"" >> $(BACKEND_CONFIG_TMP)
	@echo "region = \"$(REGION)\"" >> $(BACKEND_CONFIG_TMP)

#####################################
# Terraform commands
#####################################

terraform-init:
	@rm -rf terraform/.terraform
	terraform -chdir=terraform init -backend-config=$(notdir $(BACKEND_CONFIG_TMP))

terraform-apply:
	terraform -chdir=terraform apply -var="environment=$(ENV)" -auto-approve

#####################################
# Deploy
#####################################

deploy: zip-all generate-backend-config terraform-init terraform-apply
	@echo "🚀 Deployed $(PROJECT_NAME) to environment: $(ENV)"
