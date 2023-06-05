# Use an official Python runtime as the base image
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory in the container
WORKDIR /app

# Specify the volume to mount the data folder
VOLUME /app/data

# Set environment variables
ENV AWS_ACCESS_KEY_ID=value1 \
    AWS_SECRET_ACCESS_KEY=value2 \
    AWS_SES_REGION=value2 \
    RECIPIENT_EMAIL_ADDRESS=value2 \
    SENDER_EMAIL_ADDRESS=value2 \
    DB_USER=value2 \
    DB_PASSWORD=value2 \
    DB_HOST=value2 \
    DB_PORT=value2 \
    DB_NAME=value2  

# upgrade pip
RUN  pip install --upgrade pip

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python code into the container
COPY . ${LAMBDA_TASK_ROOT}

# Set the command to run your Python application
CMD ["lambda_function.lambda_handler" ]