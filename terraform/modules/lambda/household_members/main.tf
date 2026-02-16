module "create_member" {
  source                = "./create_member"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "create-member"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}

module "get_all_members" {
  source                = "./get_all_members"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "get-all-members"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}

module "delete_member" {
  source                = "./delete_member"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "delete-member"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}
