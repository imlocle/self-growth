data "aws_caller_identity" "current" {}

locals {
  name          = "${var.project_name}-${var.lambda_name}"
  function_name = "${local.name}-${var.environment}"
  handler_path  = replace(var.lambda_name, "-", "_")
}

#####################################
# Lambda Role
#####################################

resource "aws_iam_role" "this" {
  name = "${local.name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

#####################################
# Lambda Policy
#####################################

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.name}-lambda-policy-${var.environment}"
  role = aws_iam_role.this.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow",
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem"
        ],
        Resource = [
          "${var.self_growth_table_arn}",
          "${var.self_growth_table_arn}/*"
        ]
      }
    ]
  })
}

#####################################
# Lambda Basic Execution Role
#####################################

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

#####################################
# Lambda Function
#####################################

resource "aws_lambda_function" "this" {
  function_name = local.function_name
  handler       = "handlers.todos.${local.handler_path}.lambda_handler"
  runtime       = var.runtime
  role          = aws_iam_role.this.arn
  timeout       = 30

  filename         = "${path.root}/builds/${local.function_name}.zip"
  source_code_hash = filebase64sha256("${path.root}/builds/${local.function_name}.zip")

  layers     = [aws_lambda_layer_version.common_dependencies.arn]
  depends_on = [aws_lambda_layer_version.common_dependencies]

  environment {
    variables = {
      SELF_GROWTH_TABLE = var.self_growth_table_id
      COGNITO_CLIENT_ID = var.cognito_client_id
    }
  }
}

#####################################
# Lambda Layer
#####################################

resource "aws_lambda_layer_version" "common_dependencies" {
  filename            = "${path.root}/builds/python.zip"
  layer_name          = "${var.project_name}-common-deps"
  compatible_runtimes = [var.runtime]

  lifecycle {
    create_before_destroy = true
  }

  # 👇 Force new version on changes
  source_code_hash = filebase64sha256("${path.root}/builds/python.zip")
}

#####################################
# API Gateway Integration
#####################################

resource "aws_lambda_permission" "allow_apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "this" {
  api_id                 = var.api_id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.this.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "this" {
  api_id    = var.api_id
  route_key = "PUT /households/{householdId}/subjects/{subjectId}/todos/{todoId}"
  target    = "integrations/${aws_apigatewayv2_integration.this.id}"

  authorization_type = "JWT"
  authorizer_id      = var.authorizer_id
}

