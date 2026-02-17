output "api_id" {
  value = aws_apigatewayv2_api.this.id
}

output "api_execution_arn" {
  value = aws_apigatewayv2_api.this.execution_arn
}

output "api_endpoint" {
  value = aws_apigatewayv2_api.this.api_endpoint
}

output "authorizer_id" {
  value = aws_apigatewayv2_authorizer.cognito.id
}

output "api_log_group_name" {
  value = aws_cloudwatch_log_group.api_gateway.name
}

output "throttling_settings" {
  value = {
    burst_limit = var.throttling_burst_limit
    rate_limit  = var.throttling_rate_limit
  }
}
