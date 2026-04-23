/*
Reusable module invocation for Lambda. The actual implementation lives in
`iac/modules/lambda` so the same module can be reused to create additional
Lambda functions in the future.
*/

module "fs_lambda" {
  source = "../modules/lambda"

  function_name = "inference-api-lambda"
  source_path    = "${path.module}/lambda"
  handler       = "inference_lambda.lambda_handler"
  runtime       = "python3.13"
  source_dir = "../../backend"

  environment = {
    ENVIRONMENT = "production"
    LOG_LEVEL   = "info"
  }

  tags = {
    Environment = "production"
    Application = "fullstack-backend"
  }

  publish = false
}

output "fs_lambda_arn" {
  value = module.fs_lambda.lambda_arn
}
