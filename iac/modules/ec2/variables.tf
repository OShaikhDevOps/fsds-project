variable "instance_type" {
  default = "t3.micro"
  description = "Instance Type"
}

variable "subnet_id" {
  description = "Optional subnet id to launch the instance into (e.g. subnet-0123...)"
  type        = string
  default     = ""
}

variable "vpc_id" {
  description = "Optional VPC id (informational)"
  type        = string
  default     = "vpc-053d3afc0e87cf96a"
}

variable "vpc_security_group_ids" {
  description = "Optional list of security group ids to attach to the instance"
  type        = list(string)
  default     = []
}

variable "instance_profile" {
  description = "IAM role attachment with EC2"
  type        = string
  default     = "ec2-role"
}

variable "key_name" {
  description = "keypair to be attached"
  type        = string
  default     = "fullstack-keypair"
}