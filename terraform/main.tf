provider "aws" {
  region = "eu-west-2" 
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_cloudwatch_log_group" "etl_log_group" {
  name              = "/ecs/c14-qasim-rafiq-etl-task-def"
  retention_in_days = 7
} 

resource "aws_ecs_task_definition" "c14-qasim-rafiq-etl-task-def" {
    family                   = "c14-qasim-rafiq-etl-task-def"
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    memory                   = "3072"
    cpu                      = "1024"
    execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn
    task_role_arn = data.aws_iam_role.ecs_task_execution_role.arn

    container_definitions    = jsonencode([
    {
      name                = "c14-qasim-rafiq-etl-container"
      image               = var.ecr_repository_url
      memory              = 3072
      cpu                 = 1024
      essential           = true
      environment         = [
        { name = "DATABASE_IP", value = var.DATABASE_IP },
        { name = "DATABASE_PORT", value = var.DATABASE_PORT },
        { name = "DATABASE_NAME",   value = var.DATABASE_NAME },
        { name = "DATABASE_USERNAME", value = var.DATABASE_USERNAME },
        { name = "DATABASE_PASSWORD", value = var.DATABASE_PASSWORD },
        { name = "AWS_ACCESS_KEY_ID", value = var.AWS_ACCESS_KEY_ID},
        { name = "AWS_SECRET_ACCESS_KEY", value = var.AWS_SECRET_ACCESS_KEY},
        { name = "AWS_REGION", value = var.AWS_REGION}
      ]
      logConfiguration    = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.etl_log_group.name  
          awslogs-region        = "eu-west-2"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
  runtime_platform {
        operating_system_family = "LINUX" 
        cpu_architecture        = "X86_64" 
    }
}

data "aws_iam_policy_document" "c14-qasim-rafiq-lambda-policy" {
    statement {
        actions    = ["sts:AssumeRole"]
        effect     = "Allow"
        principals {
            type        = "Service"
            identifiers = ["lambda.amazonaws.com"]
        }
  }
}

resource "aws_iam_role" "c14-qasim-rafiq-lambda-role"{
    name= "c14-qasim-rafiq-lambda-role"
    assume_role_policy=  data.aws_iam_policy_document.c14-qasim-rafiq-lambda-policy.json

} 

resource "aws_lambda_function" "c14-qasim-rafiq-lambda-report" {
    function_name = "c14-qasim-rafiq-lambda-report"
    role = aws_iam_role.c14-qasim-rafiq-lambda-role.arn
    package_type  = "Image"
    architectures = ["x86_64"]
    image_uri = var.ecr_repo_daily

    environment {
        variables = {
            DATABASE_PORT = var.DATABASE_PORT
            DATABASE_USERNAME = var.DATABASE_USERNAME
            DATABASE_NAME = var.DATABASE_NAME
            DATABASE_IP = var.DATABASE_IP
            DATABASE_PASSWORD = var.DATABASE_PASSWORD
        }
    }

}
