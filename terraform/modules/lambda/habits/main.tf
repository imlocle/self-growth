module "create_habit" {
  source                = "./create_habit"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "create-habit"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}

module "get_habit" {
  source                = "./get_habit"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "get-habit"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
}

module "get_all_habit" {
  source                = "./get_all_habit"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "get-all-habit"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
}

module "update_habit" {
  source                = "./update_habit"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "update-habit"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
}

module "delete_habit" {
  source                = "./delete_habit"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "delete-habit"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}
