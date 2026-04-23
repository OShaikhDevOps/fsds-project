output "private_ip" {
	description = "Private IP address assigned to the instance"
	value       = aws_instance.example.private_ip
}

output "public_ip" {
	description = "Public IP address assigned to the instance (if any)"
	value       = aws_instance.example.public_ip
	sensitive   = false
}

output "instance_id" {
  description = "Instance ID of the Instance"
  value = aws_instance.example.id
}