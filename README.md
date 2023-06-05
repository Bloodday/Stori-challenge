# Steps to run the project

- Clone the repository and ensure Docker is installed on the system.

- Create an IAM user with permissions to send SES messages and generate an access key, the access key information will be used later

- In SES, if the account is in sandbox mode, you must register and verify the email that will send the email and the one that will receive the email, otherwise only the account that will send the emails should be verified.

- On your PC, if it's Windows, create a folder at c:/data, and copy the transactions.csv file located in this repository. If it's Linux, place the file in the folder of your preference and replace the path in the Volumes section of python-app in the docker-compose.yml file located inside the src folder.

- Configure the following environment variables in the docker-compose file according to the information of the IAM user you created for SES. Additionally, use the emails that you verified in SES for receiving and sending emails.

AWS_ACCESS_KEY_ID: 
AWS_SECRET_ACCESS_KEY: 
AWS_SES_REGION: us-east-1 
RECIPIENT_EMAIL_ADDRESS:  
SENDER_EMAIL_ADDRESS:  

- Once the configuration is done. In the console, navigate to the src folder and run the command docker compose up, which will create a container for the PostgreSQL database and a container for the Python application.

# How the application works

The Python application will run immediately, process any .csv file inside the folder to which you have linked the volume, and send the email. You can view the operations in the console.

To view the email, check the spam folder, as it's very likely to have ended up there. The subject of the email is "Account Balance Summary".

The application have a sleep time of 60 seconds before exit, the "docker compose up" command will restart the container after it exits and will process the csv files again, already processed transactions will be ignored using the id of the transaction.

you can press control + c to stop both containers
