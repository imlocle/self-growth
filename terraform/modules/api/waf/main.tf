resource "aws_wafv2_web_acl" "api_waf" {
  name        = "${var.project_name}-api-waf-${var.environment}"
  description = "Allow only US traffic to the API"
  scope       = "REGIONAL" # because API Gateway is regional

  default_action {
    block {}
  }

  rule {
    name     = "AllowUSOnly"
    priority = 1

    action {
      allow {}
    }

    statement {
      geo_match_statement {
        country_codes = ["US"]
      }
    }

    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project_name}-us-geo-allow-${var.environment}"
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project_name}-api-waf-${var.environment}"
    sampled_requests_enabled   = true
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
