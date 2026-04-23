data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    # broaden pattern to match Jammy (22.04), Noble (24.04), and future server images
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "example" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  # If you provide `var.subnet_id`, the instance will be launched into that subnet.
  subnet_id     = var.subnet_id
  vpc_security_group_ids = var.vpc_security_group_ids
  iam_instance_profile = var.instance_profile
  key_name = var.key_name
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name = "fullstack-project"
  }
  lifecycle {
    create_before_destroy = true
  }
}