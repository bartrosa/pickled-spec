terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_kms_key" "users" {
  description         = "Users database encryption key"
  enable_key_rotation = true
}

resource "aws_db_instance" "users" {
  identifier                = "users"
  engine                    = "postgres"
  instance_class            = "db.t3.micro"
  allocated_storage         = 20
  username                  = "admin"
  password                  = var.db_password
  storage_encrypted         = true
  kms_key_id                = aws_kms_key.users.arn
  backup_retention_period   = 7
  deletion_protection       = true
  skip_final_snapshot       = false
  final_snapshot_identifier = "users-final"
}

resource "aws_cloudwatch_log_group" "audit" {
  name              = "/app/audit"
  retention_in_days = 90
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "RDS master password for the users database instance."
}
