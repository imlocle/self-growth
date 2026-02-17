variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "cognito_user_pool_client_id" {
  type = string
}

variable "cognito_user_pool_id" {
  type = string
}

variable "throttling_burst_limit" {
  type        = number
  description = "Maximum number of concurrent requests (burst)"
  default     = 100
}

variable "throttling_rate_limit" {
  type        = number
  description = "Steady-state requests per second"
  default     = 50
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days"
  default     = 7
}
