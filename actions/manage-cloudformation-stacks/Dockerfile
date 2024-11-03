FROM python:3.8-slim

# Install dependencies
RUN pip install boto3

# Copy the script
COPY manage-cloudformation-stacks.py /manage-cloudformation-stacks.py

# Set the entrypoint
ENTRYPOINT ["python", "/manage-cloudformation-stacks.py"]