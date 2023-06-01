import boto3
from botocore.exceptions import ClientError
import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_sns_region = os.environ['AWS_SNS_REGION'] # Update with your desired region

sns_client = boto3.client('sns', region_name=aws_sns_region, aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)

sns_topic_arn = os.environ['SNS_TOPIC_ARN']  # ARN of the SNS topic to which you want to publish the email
subject = 'Your Email Subject'
message = 'Hello, this is the body of your email.'

response = sns_client.publish(TopicArn=sns_topic_arn, Message=message, Subject=subject)