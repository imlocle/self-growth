terraform {
  backend "s3" {
    bucket       = "${var.project_name}-terraform-state-bucket"
    key          = "${var.project_name}/${var.environment}/terraform.tfstate"
    region       = var.aws_region
    use_lockfile = true
  }
}
