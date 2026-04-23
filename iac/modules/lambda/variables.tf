variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "source_dir" {
  description = "Legacy: path to the Lambda source directory (relative to calling module). Kept for backward compatibility."
  type        = string
  default     = "lambda"
}

variable "source_path" {
  description = "Optional path to the Lambda source directory or file (absolute or relative). If set, this takes precedence over `source_dir`."
  type        = string
  default     = ""
}

variable "handler" {
  description = "Lambda handler"
  type        = string
  default     = "index.handler"
}

variable "runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "nodejs20.x"
}

variable "environment" {
  description = "Environment variables for the Lambda"
  type        = map(string)
  default     = {}
}

variable "tags" {
  description = "Tags to apply to the Lambda"
  type        = map(string)
  default     = {}
}

variable "role_name" {
  description = "Optional name for the generated IAM role"
  type        = string
  default     = ""
}

variable "additional_policy_arns" {
  description = "Optional list of additional managed policy ARNs to attach to the role"
  type        = list(string)
  default     = []
}

variable "publish" {
  description = "Whether to publish a new version of the Lambda"
  type        = bool
  default     = false
}

variable "output_path" {
  description = "Path where the created zip file will be written. Defaults to module folder with function name."
  type        = string
  default     = ""
}
