import boto3
import os

# Configurations
STACK_NAME_PERMISSIONS_BOUNDARY = 'question01-permissions-boundary-stack'
TEMPLATE_BODY_PERMISSIONS_BOUNDARY = open('permissions-boundary.yaml', 'r').read()
STACK_NAME_IDENTITY_BASED_POLICY = 'question01-identity-based-policy-stack'
TEMPLATE_BODY_IDENTITY_BASED_POLICY = open('identity-based-policy.yaml', 'r').read()
REGION = 'us-east-1'
USER_PASSWORD = os.getenv('USER_PASSWORD')  # get password from environment variable

# Initialize clients
cf_client = boto3.client('cloudformation', region_name=REGION)

def create_stack(stack_name, template_body):
    try:
        cf_client.describe_stacks(StackName=stack_name)
        print(f'Stack {stack_name} already exists. Updating stack...')
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
    except cf_client.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f'Criando stack {stack_name}...')
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
        else:
            raise
    waiter.wait(StackName=stack_name)
    print(f'Stack {stack_name} created/updated successfully.')

if __name__ == '__main__':
    try:
        create_stack(STACK_NAME_PERMISSIONS_BOUNDARY, TEMPLATE_BODY_PERMISSIONS_BOUNDARY)
        create_stack(STACK_NAME_IDENTITY_BASED_POLICY, TEMPLATE_BODY_IDENTITY_BASED_POLICY)
    except Exception as e:
        print(f'Erro ao criar/atualizar a stack: {e}')
        raise