module "create_habit_event" {
  source                = "./create_habit_event"
  environment           = var.environment
  runtime               = var.runtime
  lambda_name           = "create-habit-event"
  project_name          = var.project_name
  self_growth_table_arn = var.self_growth_table_arn
  self_growth_table_id  = var.self_growth_table_id
  api_execution_arn     = var.api_execution_arn
  api_id                = var.api_id
  authorizer_id         = var.authorizer_id
  cognito_client_id     = var.cognito_client_id
}
