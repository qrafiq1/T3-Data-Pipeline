variable "ecr_repository_url" {
  description = "URL of the existing ECR repository"
  type        = string
}

variable "DATABASE_IP" {
  description = "Redshift cluster host endpoint"
  type        = string
}

variable "DATABASE_PORT" {
  description = "Redshift port"
  type        = string
  default     = "5439"
}

variable "DATABASE_NAME" {
  description = "Redshift database name"
  type        = string
}

variable "DATABASE_USERNAME" {
  description = "Redshift user"
  type        = string
}

variable "DATABASE_PASSWORD" {
  description = "Redshift password"
  type        = string
  sensitive   = true
}

variable "AWS_ACCESS_KEY_ID" {
  description = "AWS key"
  type = string
  sensitive = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  description = "AWS secret key"
  type = string
  sensitive = true
}

variable "AWS_REGION" {
  description = "AWS region "
  type = string
  sensitive = true
}

variable "ecr_repo_daily" {
  description = "image for daily report"
  type = string
}