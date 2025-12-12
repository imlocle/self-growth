#####################################
# User Pool
#####################################

resource "aws_cognito_user_pool" "this" {
  name = "${var.project_name}-user-pool-${var.environment}"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  schema {
    name                = "phone_number"
    attribute_data_type = "String"
    required            = false
    mutable             = true

    string_attribute_constraints {
      min_length = 7
      max_length = 20
    }
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true

    string_attribute_constraints {
      min_length = 5
      max_length = 320
    }
  }

  schema {
    name                = "given_name"
    attribute_data_type = "String"
    required            = false
    mutable             = true

    string_attribute_constraints {
      min_length = 1
      max_length = 50
    }
  }

  schema {
    name                = "family_name"
    attribute_data_type = "String"
    required            = false
    mutable             = true

    string_attribute_constraints {
      min_length = 1
      max_length = 50
    }
  }

  # Helpful tags
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

#####################################
# User Pool Client
#####################################

resource "aws_cognito_user_pool_client" "this" {
  name         = "${var.project_name}-app-client-${var.environment}"
  user_pool_id = aws_cognito_user_pool.this.id

  generate_secret = false # true for backend-only clients

  allowed_oauth_flows_user_pool_client = true

  allowed_oauth_flows = ["code"] # Authorization Code Flow
  allowed_oauth_scopes = [
    "openid",
    "email",
    "profile",
  ]

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]

  callback_urls = var.cognito_callback_urls
  logout_urls   = var.cognito_logout_urls

  supported_identity_providers = ["COGNITO"]

  prevent_user_existence_errors = "ENABLED"

  # JWT token lifetimes
  access_token_validity  = 60
  id_token_validity      = 60
  refresh_token_validity = 30

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }
}

#####################################
# User Pool Domain
#####################################

resource "aws_cognito_user_pool_domain" "this" {
  domain       = "${var.project_name}-${var.environment}"
  user_pool_id = aws_cognito_user_pool.this.id
}


