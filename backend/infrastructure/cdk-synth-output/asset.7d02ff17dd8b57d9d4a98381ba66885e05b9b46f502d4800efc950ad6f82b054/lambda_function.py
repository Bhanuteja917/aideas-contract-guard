import json
import boto3
import os
from datetime import datetime
from uuid import uuid4

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

CONTRACTS_BUCKET = os.environ['CONTRACTS_BUCKET']
CONTRACTS_TABLE = os.environ['CONTRACTS_TABLE']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def lambda_handler(event, context):
    print(f"Upload Lambda invoked: {json.dumps(event)}")
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
    }
    
    try:
        # Get userId from Cognito authorizer
        user_id = event['requestContext']['authorizer']['claims']['sub']
        if not user_id:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        # Parse request body
        if not event.get('body'):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        body = json.loads(event['body'])
        
        # Validate input
        file_name = body.get('fileName')
        file_size = body.get('fileSize')
        content_type = body.get('contentType')
        
        if not all([file_name, file_size, content_type]):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'fileName, fileSize, and contentType are required'
                })
            }
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'File must be under 10MB'})
            }
        
        if file_size <= 0:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'File size must be greater than 0'})
            }
        
        # Validate content type
        if content_type != 'application/pdf':
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Only PDF files are supported'})
            }
        
        # Validate file extension
        if not file_name.lower().endswith('.pdf'):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Only PDF files are supported'})
            }
        
        # Generate unique contract ID
        contract_id = str(uuid4())
        s3_key = f"{user_id}/{contract_id}.pdf"
        
        # Create pre-signed URL for upload (15 minutes expiration)
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': CONTRACTS_BUCKET,
                'Key': s3_key,
                'ContentType': content_type
            },
            ExpiresIn=900
        )
        
        # Store contract metadata in DynamoDB
        table = dynamodb.Table(CONTRACTS_TABLE)
        now = datetime.utcnow().isoformat() + 'Z'
        
        table.put_item(
            Item={
                'contractId': contract_id,
                'userId': user_id,
                'fileName': file_name,
                'fileSize': file_size,
                's3Bucket': CONTRACTS_BUCKET,
                's3Key': s3_key,
                'uploadedAt': now,
                'status': 'pending_upload'
            }
        )
        
        print(f"Created contract {contract_id} for user {user_id}")
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'uploadUrl': upload_url,
                'contractId': contract_id
            })
        }
        
    except Exception as e:
        print(f"Error in upload handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
