variable "project_name" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "environment" {
  type = string
}

variable "cognito_callback_urls" {
  type        = list(string)
  description = "Allowed callback URLs for Cognito app client"
  default     = ["http://localhost:3000"] # update later for frontend
}

variable "cognito_logout_urls" {
  type        = list(string)
  description = "Allowed logout URLs for Cognito app client"
  default     = ["http://localhost:3000"]
}
