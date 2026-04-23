# Terraform Lambda Module

Usage example:

module "my_lambda" {
  source = "../../modules/lambda"

  function_name = "my-function"
  # Either set `source_dir` (legacy, relative) or `source_path` (preferred; absolute or relative)
  source_path    = "../lambda" # path to function code (preferred)
  handler       = "index.handler"
  runtime       = "nodejs20.x"

  environment = {
    ENVIRONMENT = "production"
  }

  tags = {
    Application = "example"
  }
}

Outputs:
- `lambda_arn`
- `lambda_name`
- `role_arn`
