resource "aws_s3_bucket" "logs" {
  bucket = "pickled-test-insecure-logs"
}

resource "aws_s3_bucket_acl" "logs_acl" {
  bucket = aws_s3_bucket.logs.id
  acl    = "public-read"
}
