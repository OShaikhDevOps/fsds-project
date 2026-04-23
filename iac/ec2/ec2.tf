module "ec2" {
  source = "../modules/ec2"
  subnet_id = "subnet-0390d694d79c136d5"
  vpc_security_group_ids  = ["sg-087d8b3b2626c2682"]
  instance_profile = "ec2-role"
  key_name = "fullstack-keypair"
}