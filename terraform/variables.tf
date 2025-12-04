variable "aws_region" {
  type    = string
  default = "us-west-1"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "project_name" {
  type    = string
  default = "self-growth"
}

variable "runtime" {
  type    = string
  default = "python3.13"
}
