terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_db_instance" "users" {
  identifier             = "users"
  engine                   = "postgres"
  instance_class           = "db.t3.micro"
  allocated_storage        = 20
  username                 = "admin"
  password                 = "changeme"
  skip_final_snapshot      = true
  storage_encrypted        = true
  deletion_protection      = true
}
