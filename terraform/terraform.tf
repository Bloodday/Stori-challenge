provider "aws" {
  region = "us-west-1"
}

data "aws_vpc" "my_vpc" {
  default = true
}


resource "aws_lambda_function" "stori_challenge" {
  function_name = "stori_challenge_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  timeout       = 35

  package_type  = "Image"
  image_uri = "${aws_ecr_repository.stori_challenge.repository_url}:latest"
  
  image_config {
    # use this to point to different handlers within
    # the same image, or omit `image_config` entirely
    # if only serving a single Lambda function
    command = ["lambda_function.lambda_handler"]
  }

  depends_on = [
    aws_ecr_repository.stori_challenge,
    aws_iam_role.lambda_exec_role,
    aws_iam_role_policy_attachment.lambda_vpc_exec_role_policy_attachment
  ]

  vpc_config {
    subnet_ids         = [aws_subnet.example.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }
  
  environment {
    variables = {
      DB_USER = aws_db_instance.postgres_db.username
      DB_PASSWORD = aws_db_instance.postgres_db.password
      DB_HOST = aws_db_instance.postgres_db.address
      DB_PORT = aws_db_instance.postgres_db.port
      DB_NAME = aws_db_instance.postgres_db.identifier
      AWS_SES_USER_ACCESS_KEY_ID = "value"
      AWS_SES_USER_SECRET_ACCESS_KEY = "value"
      AWS_SES_REGION = "us-east-1"
      RECIPIENT_EMAIL_ADDRESS = "email@email.com"
      SENDER_EMAIL_ADDRESS = "email2@email.com"
      PYTHONUNBUFFERED = "1"
      # Add more variables as needed
    }
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name               = "lambda_exec_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_exec_role_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}


resource "aws_db_instance" "postgres_db" {

  identifier             = "stori-db"
  allocated_storage      = 20
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "15.3"
  instance_class         = "db.t3.micro"
  username               = "dbadmin"
  password               = "dbpassword"
  publicly_accessible    = false
  skip_final_snapshot    = true
  backup_retention_period= 0
  apply_immediately      = true

  tags = {
    Name = "stori_db"
  }

  vpc_security_group_ids = [aws_security_group.db_sg.id]

}

resource "aws_subnet" "example" {
  vpc_id     = data.aws_vpc.my_vpc.id
  cidr_block = "172.31.32.0/20"
}

resource "aws_security_group" "lambda_sg" {
  name   = "lambda_sg"
  vpc_id = data.aws_vpc.my_vpc.id
}

resource "aws_security_group" "db_sg" {
  name   = "db_sg"
  vpc_id = data.aws_vpc.my_vpc.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.lambda_sg.id]
  }
}

resource "aws_ecr_repository" "stori_challenge" {
  name = "stori_challenge"
}


output "lambda_function_arn" {
  value = aws_lambda_function.stori_challenge.arn
}