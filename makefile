# Self-Growth Makefile (incremental, fast-by-default, with convenience targets)
#
# Common usage:
#   make deploy ENV=dev
#   make deploy ENV=prod
#
# Build only one lambda zip:
#   make zip-create-todo ENV=dev
#
# Deploy only one lambda (build its zip, then terraform apply):
#   make deploy-create-todo ENV=dev
#
# Force rebuild layer:
#   make rebuild-layer ENV=dev
#
# Full reset:
#   make nuke && make deploy ENV=dev

.PHONY: deploy clean nuke check-aws-credentials \
        zip-all zip-layer generate-backend-config terraform-init terraform-apply \
        rebuild-layer rebuild-zips \
        $(LAMBDAS:%=zip-%) $(LAMBDAS:%=deploy-%)

#####################################
# Config
#####################################

ENV ?= dev
PROJECT_NAME = self-growth
REGION = us-west-1

TERRAFORM_DIR = terraform
BUILD_DIR = $(TERRAFORM_DIR)/builds

LAYER_DIR = lambda_layer/python
LAYER_ZIP = $(BUILD_DIR)/python.zip
BACKEND_CONFIG_TMP = $(TERRAFORM_DIR)/backend.auto.hcl

# List all Lambda logical names (WITHOUT env suffix or .zip)
LAMBDAS = create-todo get-todo get-all-todo update-todo delete-todo \
          create-habit get-habit get-all-habit update-habit delete-habit \
          create-habit-event get-habit-event get-all-habit-events get-habit-analytics \
          signup login confirm-signup refresh-token \
          create-user-profile get-user-profile \
          create-household get-household get-all-households update-household delete-household \
          create-member get-all-members delete-member \
          create-subject get-subject get-all-subjects update-subject delete-subject

PYTHON_LAYER_IMAGE = public.ecr.aws/sam/build-python3.13
REQ_FILE = src/requirements.txt

# All source files (used as a coarse dependency signal for zips)
# NOTE: This will rebuild ALL lambda zips when any src file changes.
SRC_FILES := $(shell find src -type f)

#####################################
# Ensure build directory exists
#####################################

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

#####################################
# Clean / Nuke
#####################################

# Removes build artifacts only (keeps terraform init cache + providers)
clean:
	rm -f $(BUILD_DIR)/*.zip $(BACKEND_CONFIG_TMP)
	rm -rf $(LAYER_DIR)

# Full reset (use when terraform init/cache gets weird)
nuke: clean
	rm -rf $(TERRAFORM_DIR)/.terraform $(TERRAFORM_DIR)/.terraform.lock.hcl

#####################################
# AWS Credentials Check
#####################################

check-aws-credentials:
	@echo "🔍 Checking AWS credentials..."
	@if [ -z "$$AWS_PROFILE" ] && [ -z "$$AWS_ACCESS_KEY_ID" ]; then \
		echo "❌ ERROR: AWS credentials not configured!"; \
		echo ""; \
		echo "Please configure AWS credentials using one of these methods:"; \
		echo ""; \
		echo "Option 1: Use AWS CLI profile"; \
		echo "  export AWS_PROFILE=default"; \
		echo "  export AWS_REGION=$(REGION)"; \
		echo ""; \
		echo "Option 2: Use environment variables"; \
		echo "  export AWS_ACCESS_KEY_ID=your-key"; \
		echo "  export AWS_SECRET_ACCESS_KEY=your-secret"; \
		echo "  export AWS_REGION=$(REGION)"; \
		echo ""; \
		echo "Option 3: Disable IMDS and use AWS CLI"; \
		echo "  export AWS_EC2_METADATA_DISABLED=true"; \
		echo "  export AWS_PROFILE=default"; \
		echo "  export AWS_REGION=$(REGION)"; \
		echo ""; \
		echo "Verify with: aws sts get-caller-identity"; \
		exit 1; \
	fi
	@aws sts get-caller-identity > /dev/null 2>&1 || \
		(echo "❌ ERROR: AWS credentials are invalid or AWS CLI is not configured" && \
		 echo "Run: aws configure" && exit 1)
	@echo "✅ AWS credentials verified"

#####################################
# Backend config (file target)
#####################################

# Create backend config file (only updates if target is missing or ENV changes via nuke/clean)
$(BACKEND_CONFIG_TMP):
	@echo "bucket = \"$(PROJECT_NAME)-terraform-state-bucket\"" > $(BACKEND_CONFIG_TMP)
	@echo "key    = \"$(PROJECT_NAME)/$(ENV)/terraform.tfstate\"" >> $(BACKEND_CONFIG_TMP)
	@echo "region = \"$(REGION)\"" >> $(BACKEND_CONFIG_TMP)

generate-backend-config: $(BACKEND_CONFIG_TMP)

#####################################
# Lambda Layer (incremental)
#####################################

# Marker file to avoid re-installing deps when requirements.txt hasn't changed
$(LAYER_DIR)/.built: $(REQ_FILE)
	rm -rf $(LAYER_DIR)
	mkdir -p $(LAYER_DIR)
	docker run --rm \
		--platform linux/amd64 \
		-v $(CURDIR)/src:/var/task \
		-v $(CURDIR)/$(LAYER_DIR):/lambda/python \
		$(PYTHON_LAYER_IMAGE) \
		/bin/sh -c "pip3 install -r /var/task/requirements.txt -t /lambda/python --no-cache-dir"
	@touch $@

# Zip the layer only when deps were rebuilt
$(LAYER_ZIP): $(BUILD_DIR) $(LAYER_DIR)/.built
	cd lambda_layer && zip -r ../$(LAYER_ZIP) python > /dev/null

zip-layer: $(LAYER_ZIP)

#####################################
# Lambda zips (incremental)
#####################################

# File target for each lambda zip
# Produces: terraform/builds/self-growth-<lambda>-<env>.zip
$(BUILD_DIR)/$(PROJECT_NAME)-%-$(ENV).zip: $(BUILD_DIR) $(SRC_FILES)
	cd src && zip -r ../$@ . > /dev/null

# Convenience: "make zip-create-todo ENV=dev"
zip-%: $(BUILD_DIR)/$(PROJECT_NAME)-%-$(ENV).zip
	@echo "✅ Built $<"

# Zip all lambdas + layer (only rebuilds stale outputs)
zip-all: zip-layer $(LAMBDAS:%=$(BUILD_DIR)/$(PROJECT_NAME)-%-$(ENV).zip)

#####################################
# Terraform commands (incremental)
#####################################

terraform-init: check-aws-credentials $(BACKEND_CONFIG_TMP)
	terraform -chdir=$(TERRAFORM_DIR) init -backend-config=$(notdir $(BACKEND_CONFIG_TMP))

terraform-apply:
	terraform -chdir=$(TERRAFORM_DIR) apply -var="environment=$(ENV)" -auto-approve

#####################################
# Deploy
#####################################

deploy: zip-all terraform-init terraform-apply
	@echo "🚀 Deployed $(PROJECT_NAME) to environment: $(ENV)"

# Convenience: deploy a single lambda zip, then apply
# (Terraform will update only what changed via source_code_hash)
deploy-%: zip-% terraform-init terraform-apply
	@echo "🚀 Deployed lambda '$*' to environment: $(ENV)"

#####################################
# Force rebuild helpers
#####################################

# Rebuild only the layer (use when requirements.txt changed or you suspect layer issues)
rebuild-layer:
	rm -f $(LAYER_DIR)/.built $(LAYER_ZIP)
	$(MAKE) zip-layer ENV=$(ENV)

# Rebuild all lambda zip artifacts (use when packaging got weird)
rebuild-zips:
	rm -f $(BUILD_DIR)/$(PROJECT_NAME)-*-$(ENV).zip
	$(MAKE) zip-all ENV=$(ENV)
