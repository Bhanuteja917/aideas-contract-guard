import json
import boto3
import os
from datetime import datetime
from uuid import uuid4

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

CONTRACTS_BUCKET = os.environ['CONTRACTS_BUCKET']
CONTRACTS_TABLE = os.environ['CONTRACTS_TABLE']
ANALYSES_TABLE = os.environ.get('ANALYSES_TABLE', '')
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
        # Get HTTP method
        http_method = event.get('httpMethod', 'POST')
        
        # Route based on HTTP method and path
        path = event.get('path', '')
        
        if http_method == 'GET':
            # Check if it's a list or get single contract
            if path.endswith('/contracts') or '/contracts/' not in path:
                return handle_list_contracts(event, headers)
            else:
                return handle_get_contract(event, headers)
        elif http_method == 'POST':
            return handle_upload(event, headers)
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        print(f"Error in lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def handle_list_contracts(event, headers):
    """Handle GET /contracts - list all contracts for the user"""
    try:
        # Get userId from Cognito authorizer
        user_id = event['requestContext']['authorizer']['claims']['sub']
        if not user_id:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        # Query contracts by userId
        contracts_table = dynamodb.Table(CONTRACTS_TABLE)
        response = contracts_table.query(
            IndexName='userId-uploadedAt-index',
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False  # Sort by uploadedAt descending (newest first)
        )
        
        contracts = response.get('Items', [])
        
        # Convert Decimals to float
        contracts = [convert_decimals(contract) for contract in contracts]
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'contracts': contracts
            })
        }
        
    except Exception as e:
        print(f"Error listing contracts: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def handle_get_contract(event, headers):
    """Handle GET /contracts/{contractId} - fetch contract and analysis"""
    try:
        # Get userId from Cognito authorizer
        user_id = event['requestContext']['authorizer']['claims']['sub']
        if not user_id:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        # Get contractId from path parameters
        contract_id = event.get('pathParameters', {}).get('contractId')
        if not contract_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'contractId is required'})
            }
        
        # Fetch contract from DynamoDB
        contracts_table = dynamodb.Table(CONTRACTS_TABLE)
        contract_response = contracts_table.get_item(Key={'contractId': contract_id})
        
        if 'Item' not in contract_response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Contract not found'})
            }
        
        contract = contract_response['Item']
        
        # Verify user owns this contract
        if contract.get('userId') != user_id:
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({'error': 'Access denied'})
            }
        
        # Fetch analysis if available
        analysis = None
        if ANALYSES_TABLE:
            analyses_table = dynamodb.Table(ANALYSES_TABLE)
            analysis_response = analyses_table.query(
                IndexName='contractId-index',
                KeyConditionExpression='contractId = :cid',
                ExpressionAttributeValues={':cid': contract_id},
                Limit=1
            )
            
            if analysis_response.get('Items'):
                analysis = analysis_response['Items'][0]
                # Convert Decimal to float for JSON serialization
                analysis = convert_decimals(analysis)
        
        # Convert contract Decimals to float
        contract = convert_decimals(contract)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'contract': contract,
                'analysis': analysis
            })
        }
        
    except Exception as e:
        print(f"Error fetching contract: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def handle_upload(event, headers):
    """Handle POST /contracts/upload - create pre-signed URL"""
    
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


def convert_decimals(obj):
    """Convert Decimal objects to float for JSON serialization"""
    from decimal import Decimal
    
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    return obj
