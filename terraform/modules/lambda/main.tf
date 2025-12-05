module "create_todo" {
  source                = "./create_todo"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "create-todo"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
}

module "get_todo" {
  source                = "./get_todo"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "get-todo"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
}

module "get_all_todo" {
  source                = "./get_all_todo"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "get-all-todo"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
}

