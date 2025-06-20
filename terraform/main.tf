provider "aws" {
  region = "us-east-1"
}

# Security Group allowing SSH and app traffic
resource "aws_security_group" "invento_sg" {
  name        = "invento-sg"
  description = "Allow SSH and app access"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "invento" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.nano"
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.invento_sg.id]

  tags = {
    Name = "InventoWareApp"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
      "sudo yum install -y docker git",
      "sudo systemctl start docker",
      "sudo usermod -aG docker ec2-user"
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("C:/Users/Anuj/.ssh/invento.pem")
      host        = self.public_ip
    }
  }
}
