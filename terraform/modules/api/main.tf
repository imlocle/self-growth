module "self_growth_api" {
  source                      = "./self_growth_api"
  environment                 = var.environment
  project_name                = var.project_name
  aws_region                  = var.aws_region
  cognito_user_pool_client_id = var.cognito_user_pool_client_id
  cognito_user_pool_id        = var.cognito_user_pool_id
}
