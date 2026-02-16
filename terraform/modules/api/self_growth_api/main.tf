resource "aws_apigatewayv2_api" "this" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_headers  = ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
    allow_methods  = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_origins  = ["*"]
    expose_headers = ["Content-Type", "X-Amz-Date"]
    max_age        = 3600
  }
}

resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id          = aws_apigatewayv2_api.this.id
  name            = "${var.project_name}-cognito-authorizer-${var.environment}"
  authorizer_type = "JWT"

  identity_sources = ["$request.header.Authorization"]

  jwt_configuration {
    audience = [var.cognito_user_pool_client_id]
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${var.cognito_user_pool_id}"
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = var.environment
  auto_deploy = true
}

