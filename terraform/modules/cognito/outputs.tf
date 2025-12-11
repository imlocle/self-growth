
output "cognito_user_pool_id" {
  value       = aws_cognito_user_pool.this.id
  description = "Cognito User Pool ID"
}

output "cognito_user_pool_arn" {
  value       = aws_cognito_user_pool.this.arn
  description = "Cognito User Pool ARN"
}

output "cognito_user_pool_client_id" {
  value       = aws_cognito_user_pool_client.this.id
  description = "Cognito App Client ID"
}

output "cognito_user_pool_domain" {
  value       = aws_cognito_user_pool_domain.this.domain
  description = "Cognito Hosted UI domain prefix"
}
