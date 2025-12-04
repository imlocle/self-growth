module "lambda_1" {
  source            = "./lambda_1"
  environment       = var.environment
  runtime           = var.runtime
  lambda_name       = "lambda_1"
  project_name      = var.project_name
  table_1_table_arn = var.table_1_table_arn
  table_1_table_id  = var.table_1_table_id
  api_execution_arn = var.api_execution_arn
  api_id            = var.api_id
}
