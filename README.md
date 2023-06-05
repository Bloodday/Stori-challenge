# Disclaimer
This is not a working application, the working application lives in the "local-challenge" branch, go there and follow the Readme.md file instructions to run the program.

This repository contains the progress to deploy the python program in a lambda using docker,  ECR github actions and terraform. the terraform file creates the required infrastructure, the github actions to deploy a new image and update the lambda with any change in the repository but I couldn't connect the lambda with the database, you are free to inspect the code. 

# Steps to deploy the application:

- Fork the repository and clone it (the fork is for github actions to run)

- Verify that you have AWS CLI, Docker and Terraform installed

- Create an IAM user with permissions to send SES messages and generate an access key, the access key information will be used later

- In SES, if the account is in sandbox mode, you must register and verify the email that will send the email and the one that will receive the email, otherwise only the account that will send the emails should be verified.

- Create an IAM user with permissions to access the ECR, this permissions are needed to allow github actions pussh the image to the ECR

- create the following variables in the repository secrets for actions, this is the information of the access key from the user that can access to ECR:
	AWS_ACCESS_KEY_ID
	AWS_SECRET_ACCESS_KEY
	AWS_DEFAULT_REGION

- With the user that have permissions for SES fill the following enviroment variables in the  terraform.tf file in the terraform folder:
      AWS_SES_USER_ACCESS_KEY_ID = "value"
      AWS_SES_USER_SECRET_ACCESS_KEY = "value"
      AWS_SES_REGION = "us-east-1"
      RECIPIENT_EMAIL_ADDRESS = "email@email.com"
      SENDER_EMAIL_ADDRESS = "email2@email.com"

- Now with open a console in the Terraform folder and run the following commands
    terraform init
    terraform plan -target="aws_ecr_repository.stori_challenge"
    terraform apply -target="aws_ecr_repository.stori_challenge"

  Tthis will create the ecr repository.

- Run the Github action to compile and push the image to ECR,the github action have a second step that deploy the image to the lambda, this will fails, that's normal since the lambda doesn't exist yet.

- Now that you have the image in the ECR, run the following commands in the console to theploye the rest of the infrastructure:
    terraform init
    terraform plan 
    terraform apply

now you have the database, and the lambda created, you can go to the lambda section in the AWS console and test it there, but the connection with the database will timeout after 10 seconds.
