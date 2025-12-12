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

module "cognito" {
  source       = "./modules/cognito"
  environment  = var.environment
  project_name = var.project_name
  aws_region   = var.aws_region
}

module "dynamodb" {
  source       = "./modules/dynamodb"
  environment  = var.environment
  project_name = var.project_name
}

module "api" {
  source                      = "./modules/api"
  environment                 = var.environment
  project_name                = var.project_name
  aws_region                  = var.aws_region
  cognito_user_pool_client_id = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id        = module.cognito.cognito_user_pool_id
}

module "lambda" {
  source                = "./modules/lambda"
  environment           = var.environment
  project_name          = var.project_name
  self_growth_table_arn = module.dynamodb.self_growth_table_arn
  self_growth_table_id  = module.dynamodb.self_growth_table_id
  api_execution_arn     = module.api.self_growth_api_execution_arn
  api_id                = module.api.self_growth_api_id
  runtime               = var.runtime
  authorizer_id         = module.api.authorizer_id
  cognito_client_id     = module.cognito.cognito_user_pool_client_id
}
