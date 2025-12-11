module "aws_waf" {
  source       = "./waf"
  environment  = var.environment
  project_name = var.project_name
}

module "self_growth_api" {
  source                      = "./self_growth_api"
  environment                 = var.environment
  project_name                = var.project_name
  aws_region                  = var.aws_region
  cognito_user_pool_client_id = var.cognito_user_pool_client_id
  cognito_user_pool_id        = var.cognito_user_pool_id
  aws_wafv2_web_acl_arn       = module.aws_waf.aws_wafv2_web_acl_arn
}
