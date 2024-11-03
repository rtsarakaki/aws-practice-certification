import boto3
import os
from botocore.exceptions import ClientError

# Configurations
STACK_NAME_PERMISSIONS_BOUNDARY = 'question01-permissions-boundary-stack'
TEMPLATE_BODY_PERMISSIONS_BOUNDARY = open('permissions-boundary.yaml', 'r').read()
STACK_NAME_IDENTITY_BASED_POLICY = 'question01-identity-based-policy-stack'
TEMPLATE_BODY_IDENTITY_BASED_POLICY = open('identity-based-policy.yaml', 'r').read()
STACK_NAME_ACL = 'question01-acl'
TEMPLATE_BODY_ACL = open('acl.yaml', 'r').read()
REGION = os.getenv('AWS_REGION')  # Get region from environment variable
USER_PASSWORD = os.getenv('USER_PASSWORD')  # Get password from environment variable

# Initialize clients
cf_client = boto3.client('cloudformation', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)

def create_stack(stack_name, template_body):
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

def upload_objects_with_acl():
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    bucket_with_acl = f'example-bucket-with-acl-{account_id}'
    bucket_without_acl = f'example-bucket-without-acl-{account_id}'

    # Configure OwnershipControls to allow ACLs on the bucket with ACL
    s3_client.put_bucket_ownership_controls(
        Bucket=bucket_with_acl,
        OwnershipControls={
            'Rules': [
                {
                    'ObjectOwnership': 'ObjectWriter'
                }
            ]
        }
    )

    # Create a sample file to upload
    with open('test-file.txt', 'w') as f:
        f.write('This is a test file')

    # Check if the object already exists in the bucket with ACL
    try:
        s3_client.head_object(Bucket=bucket_with_acl, Key='test-file.txt')
        print(f'Object test-file.txt already exists in bucket {bucket_with_acl}. Upload will not be performed.')
    except ClientError:
        # Upload the file to the bucket with ACL, setting ACLs on the object
        s3_client.upload_file('test-file.txt', bucket_with_acl, 'test-file.txt', ExtraArgs={'ACL': 'public-read'})

    # Check if the object already exists in the bucket without ACL
    try:
        s3_client.head_object(Bucket=bucket_without_acl, Key='test-file.txt')
        print(f'Object test-file.txt already exists in bucket {bucket_without_acl}. Upload will not be performed.')
    except ClientError:
        # Upload the file to the bucket without ACL
        s3_client.upload_file('test-file.txt', bucket_without_acl, 'test-file.txt')

    # Delete the created file
    os.remove('test-file.txt')

if __name__ == '__main__':
    try:
        create_stack(STACK_NAME_PERMISSIONS_BOUNDARY, TEMPLATE_BODY_PERMISSIONS_BOUNDARY)
        create_stack(STACK_NAME_IDENTITY_BASED_POLICY, TEMPLATE_BODY_IDENTITY_BASED_POLICY)
        create_stack(STACK_NAME_ACL, TEMPLATE_BODY_ACL)
        upload_objects_with_acl()
        
    except Exception as e:
        print(f'Error creating/updating the stack: {e}')
        raise