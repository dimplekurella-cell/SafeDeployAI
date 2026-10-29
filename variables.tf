
variable "aws_region" {
  description = "AWS region for SafeDeploy AI"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Name of the capstone project"
  type        = string
  default     = "safedeploy-ai"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}
