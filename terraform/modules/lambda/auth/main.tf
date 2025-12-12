module "signup" {
  source            = "./signup"
  environment       = var.environment
  project_name      = var.project_name
  runtime           = var.runtime
  lambda_name       = "signup"
  api_execution_arn = var.api_execution_arn
  api_id            = var.api_id
  cognito_client_id = var.cognito_client_id
}

module "login" {
  source            = "./login"
  environment       = var.environment
  project_name      = var.project_name
  runtime           = var.runtime
  lambda_name       = "login"
  api_execution_arn = var.api_execution_arn
  api_id            = var.api_id
  cognito_client_id = var.cognito_client_id
}
