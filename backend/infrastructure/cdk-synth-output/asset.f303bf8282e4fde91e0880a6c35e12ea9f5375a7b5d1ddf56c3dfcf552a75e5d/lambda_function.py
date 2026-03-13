import json
import boto3
import os
from datetime import datetime
from urllib.parse import unquote_plus
import PyPDF2
from io import BytesIO

s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')

CONTRACTS_BUCKET = os.environ['CONTRACTS_BUCKET']
CONTRACTS_TABLE = os.environ['CONTRACTS_TABLE']
ANALYSES_TABLE = os.environ['ANALYSES_TABLE']
MAX_RETRIES = 3

def lambda_handler(event, context):
    print(f"Analyze Lambda invoked: {json.dumps(event)}")
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        print(f"Processing file: {bucket}/{key}")
        
        try:
            # Extract contractId from S3 key (format: userId/contractId.pdf)
            contract_id = key.split('/')[1].replace('.pdf', '')
            if not contract_id:
                print(f"Invalid S3 key format: {key}")
                continue
            
            # Find contract record in DynamoDB
            contract = get_contract_by_id(contract_id)
            if not contract:
                print(f"Contract not found: {contract_id}")
                continue
            
            # Update contract status to "upload_completed"
            update_contract_status(contract_id, 'upload_completed')
            print(f"Updated contract {contract_id} status to upload_completed")
            
            # Update contract status to "analyzing"
            update_contract_status(contract_id, 'analyzing')
            print(f"Updated contract {contract_id} status to analyzing")
            
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(bucket, key)
            print(f"Extracted {len(extracted_text)} characters from {key}")
            
            # TODO: Tasks 9-11 will implement:
            # - Entity identification with Comprehend
            # - Clause analysis with Bedrock
            # - Risk scoring
            # - Compliance checking
            # - Store analysis results
            
            # Update contract status to "completed" (temporary)
            update_contract_status(contract_id, 'completed')
            print(f"Analysis completed for contract {contract_id}")
            
        except Exception as e:
            print(f"Error processing {key}: {str(e)}")
            
            # Extract contractId for error handling
            try:
                contract_id = key.split('/')[1].replace('.pdf', '')
                if contract_id:
                    update_contract_status(contract_id, 'failed')
            except:
                pass
            
            raise e

def get_contract_by_id(contract_id):
    """Fetch contract from DynamoDB"""
    try:
        table = dynamodb.Table(CONTRACTS_TABLE)
        response = table.get_item(Key={'contractId': contract_id})
        return response.get('Item')
    except Exception as e:
        print(f"Error fetching contract: {str(e)}")
        raise e

def update_contract_status(contract_id, status):
    """Update contract status in DynamoDB"""
    try:
        table = dynamodb.Table(CONTRACTS_TABLE)
        now = datetime.utcnow().isoformat() + 'Z'
        
        table.update_item(
            Key={'contractId': contract_id},
            UpdateExpression='SET #status = :status, updatedAt = :updatedAt',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': status,
                ':updatedAt': now
            }
        )
    except Exception as e:
        print(f"Error updating contract status: {str(e)}")
        raise e

def extract_text_from_pdf(bucket, key):
    """
    Extract text from PDF using PyPDF2 as primary method,
    with Textract as fallback for scanned documents
    """
    try:
        # Download PDF from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        pdf_content = response['Body'].read()
        
        # Try PyPDF2 first (works with most PDFs)
        print(f"Attempting text extraction with PyPDF2 for {key}")
        pdf_file = BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if text.strip():
            print(f"Successfully extracted {len(text)} characters with PyPDF2")
            return text
        
        # If PyPDF2 returns empty (scanned document), try Textract
        print(f"PyPDF2 returned empty text, trying Textract for {key}")
        return extract_text_with_textract(bucket, key)
        
    except Exception as e:
        print(f"PyPDF2 extraction failed: {str(e)}, trying Textract")
        return extract_text_with_textract(bucket, key)

def extract_text_with_textract(bucket, key):
    """Fallback to Textract for scanned documents"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Textract attempt {attempt}/{MAX_RETRIES} for {key}")
            
            response = textract_client.detect_document_text(
                Document={'S3Object': {'Bucket': bucket, 'Name': key}}
            )
            
            # Extract text from blocks
            text_blocks = [
                block['Text'] 
                for block in response.get('Blocks', []) 
                if block['BlockType'] == 'LINE'
            ]
            extracted_text = '\n'.join(text_blocks)
            
            if not extracted_text:
                raise Exception('No text extracted from document')
            
            print(f"Successfully extracted {len(extracted_text)} characters with Textract on attempt {attempt}")
            return extracted_text
            
        except Exception as e:
            error_message = str(e)
            print(f"Textract attempt {attempt} failed: {error_message}")
            
            if 'UnsupportedDocumentException' in error_message or 'unsupported document format' in error_message:
                raise Exception('PDF format not supported by Textract. Text extraction failed.')
            
            if attempt < MAX_RETRIES:
                import time
                delay = 2 ** (attempt - 1)  # Exponential backoff
                print(f"Retrying in {delay}s...")
                time.sleep(delay)
    
    raise Exception(f'Text extraction failed after {MAX_RETRIES} attempts')
