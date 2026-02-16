module "create_household" {
  source                = "./create_household"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "create-household"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}

module "get_household" {
  source                = "./get_household"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "get-household"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}

module "get_all_households" {
  source                = "./get_all_households"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "get-all-households"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}

module "update_household" {
  source                = "./update_household"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "update-household"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}

module "delete_household" {
  source                = "./delete_household"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "delete-household"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}
