terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "dynamodb" {
  source      = "./modules/dynamodb"
  environment = var.environment
}

module "api" {
  source       = "./modules/api"
  environment  = var.environment
  project_name = var.project_name
}

module "lambda" {
  source            = "./modules/lambda"
  environment       = var.environment
  project_name      = var.project_name
  table_1_table_arn = module.dynamodb.table_1_table_arn
  table_1_table_id  = module.dynamodb.table_1_table_id
  api_execution_arn = module.api.api_1_execution_arn
  api_id            = module.api.api_1_id
  runtime           = var.runtime
}
