output "instance_public_ip" {
  description = "Public IP of EC2 Instance"
  value       = aws_instance.invento.public_ip
}
