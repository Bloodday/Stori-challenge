import boto3
from botocore.exceptions import ClientError
import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_ses_region = os.environ['AWS_SES_REGION'] # Update with your desired region

ses_client = boto3.client('ses', region_name=aws_ses_region, aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)

# Define email parameters
sender = os.environ['SENDER_EMAIL_ADDRESS']
recipient = os.environ['RECIPIENT_EMAIL_ADDRESS']
subject = 'Account Balance Summary'

def SendEmail(message):
    # Send email
    try:
        response = ses_client.send_email(
        Source=sender,
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': message}}
        }
    )
        print("Email sent successfully.")
    except ClientError as e:
        print(f"Error occurred while sending email: {e.response['Error']['Message']}")