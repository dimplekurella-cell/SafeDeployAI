
output "s3_bucket_name" {
  description = "Name of the SafeDeploy AI artifacts bucket"
  value       = aws_s3_bucket.artifacts.bucket
}

output "aws_region" {
  description = "AWS deployment region"
  value       = var.aws_region
}
