output "lambda_arn" {
  description = "ARN of the created Lambda function"
  value       = aws_lambda_function.this.arn
}

output "lambda_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.this.function_name
}

output "role_arn" {
  description = "ARN of the IAM role created for the Lambda"
  value       = aws_iam_role.this.arn
}
