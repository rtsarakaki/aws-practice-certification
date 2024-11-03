import boto3
import os
import sys
from botocore.exceptions import ClientError

def create_stack(stack_name, template_path):
    # Get region and password from environment variables
    REGION = os.getenv('AWS_REGION')
    USER_PASSWORD = os.getenv('USER_PASSWORD')

    # Read the template body
    with open(template_path, 'r') as file:
        template_body = file.read()

    # Initialize CloudFormation client
    cf_client = boto3.client('cloudformation', region_name=REGION)

    try:
        cf_client.describe_stacks(StackName=stack_name)
        print(f'Stack {stack_name} already exists. Updating stack...')
        try:
            cf_client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'UserPassword',
                        'ParameterValue': USER_PASSWORD,
                        'UsePreviousValue': False
                    }
                ],
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            waiter = cf_client.get_waiter('stack_update_complete')
            waiter.wait(StackName=stack_name)
            print(f'Stack {stack_name} updated successfully.')
        except ClientError as e:
            if 'No updates are to be performed' in str(e):
                print(f'Stack {stack_name} has no updates to be performed.')
            else:
                raise
    except cf_client.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f'Creating stack {stack_name}...')
            cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'UserPassword',
                        'ParameterValue': USER_PASSWORD
                    }
                ],
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            waiter = cf_client.get_waiter('stack_create_complete')
            waiter.wait(StackName=stack_name)
            print(f'Stack {stack_name} created successfully.')
        else:
            raise

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python manage-cloudformation-stacks.py <stack_name> <template_path>")
        sys.exit(1)

    stack_name = sys.argv[1]
    template_path = sys.argv[2]

    try:
        create_stack(stack_name, template_path)
    except Exception as e:
        print(f'Error creating/updating the stack: {e}')
        raise