import json
import boto3
import os
from datetime import datetime
from urllib.parse import unquote_plus
import PyPDF2
from io import BytesIO
from decimal import Decimal
# Model: Amazon Nova Pro

s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
comprehend_client = boto3.client('comprehend')
bedrock_client = boto3.client('bedrock-runtime')
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
            
            # Identify entities using Amazon Comprehend
            entities = identify_entities(extracted_text)
            print(f"Identified {len(entities)} entities from contract text")
            
            # Analyze clauses and calculate risk scores using Bedrock
            analysis_result = analyze_contract_with_bedrock(extracted_text, entities)
            print(f"Completed clause analysis with overall risk score: {analysis_result['overall_risk_score']}")
            
            # Generate explanations for clauses
            clauses_with_explanations = generate_clause_explanations(analysis_result['clauses'])
            print(f"Generated explanations for {len(clauses_with_explanations)} clauses")
            
            # Check compliance with Indian Contract Act
            compliance_issues = check_indian_contract_act_compliance(extracted_text)
            print(f"Identified {len(compliance_issues)} compliance issues")
            
            # Generate negotiation recommendations for high-risk clauses
            recommendations = generate_negotiation_recommendations(clauses_with_explanations)
            print(f"Generated {len(recommendations)} negotiation recommendations")
            
            # Store complete analysis in DynamoDB
            analysis_id = store_analysis_results(
                contract_id,
                contract['userId'],
                extracted_text,
                entities,
                clauses_with_explanations,
                analysis_result['risk_categories'],
                analysis_result['overall_risk_score'],
                compliance_issues,
                recommendations
            )
            print(f"Stored analysis results with ID: {analysis_id}")
            
            # Update contract status to "completed"
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

def identify_entities(text):
    """
    Identify entities in contract text using Amazon Comprehend.
    Returns list of entities with text, type, score, and position offsets.
    
    Comprehend has a 5000 byte limit per request, so we chunk large texts.
    """
    try:
        entities = []
        
        # Comprehend has a 5000 byte limit, chunk text if needed
        max_bytes = 5000
        text_bytes = text.encode('utf-8')
        
        if len(text_bytes) <= max_bytes:
            # Text fits in single request
            response = comprehend_client.detect_entities(
                Text=text,
                LanguageCode='en'
            )
            entities = response.get('Entities', [])
        else:
            # Split text into chunks at sentence boundaries
            chunks = chunk_text(text, max_bytes)
            offset = 0
            
            for chunk in chunks:
                response = comprehend_client.detect_entities(
                    Text=chunk,
                    LanguageCode='en'
                )
                
                # Adjust offsets for chunk position in original text
                chunk_entities = response.get('Entities', [])
                for entity in chunk_entities:
                    entity['BeginOffset'] += offset
                    entity['EndOffset'] += offset
                    entities.append(entity)
                
                offset += len(chunk)
        
        # Filter and format entities
        formatted_entities = []
        for entity in entities:
            # Only include relevant entity types
            if entity['Type'] in ['PERSON', 'DATE', 'QUANTITY', 'ORGANIZATION', 'LOCATION', 'COMMERCIAL_ITEM', 'EVENT', 'TITLE']:
                formatted_entities.append({
                    'text': entity['Text'],
                    'type': entity['Type'],
                    'score': round(entity['Score'], 3),
                    'beginOffset': entity['BeginOffset'],
                    'endOffset': entity['EndOffset']
                })
        
        print(f"Detected {len(formatted_entities)} entities: {', '.join([e['type'] for e in formatted_entities[:10]])}")
        return formatted_entities
        
    except Exception as e:
        print(f"Error identifying entities: {str(e)}")
        # Return empty list on error, don't fail the entire analysis
        return []

def chunk_text(text, max_bytes):
    """
    Split text into chunks that fit within byte limit.
    Tries to split at sentence boundaries to preserve context.
    """
    chunks = []
    sentences = text.split('. ')
    current_chunk = ""
    
    for sentence in sentences:
        # Add period back (except for last sentence)
        sentence_with_period = sentence if sentence == sentences[-1] else sentence + '. '
        
        # Check if adding this sentence would exceed limit
        test_chunk = current_chunk + sentence_with_period
        if len(test_chunk.encode('utf-8')) > max_bytes:
            # Current chunk is full, save it and start new one
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence_with_period
        else:
            current_chunk = test_chunk
    
    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def analyze_contract_with_bedrock(text, entities):
    """
    Analyze contract using Amazon Bedrock with Claude model.
    Identifies risky clauses and calculates risk scores.
    """
    try:
        # Prepare entity summary for context
        entity_summary = format_entities_for_prompt(entities)
        
        # Create analysis prompt
        prompt = create_contract_analysis_prompt(text, entity_summary)
        
        # Call Bedrock with Amazon Nova model
        model_id = "amazon.nova-pro-v1:0"
        
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 4000,
                "temperature": 0.3
            }
        }
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response - Nova format
        response_body = json.loads(response['body'].read())
        analysis_text = response_body['output']['message']['content'][0]['text']
        
        # Parse the structured analysis from the model's response
        analysis_result = parse_bedrock_analysis(analysis_text)
        
        return analysis_result
        
    except Exception as e:
        print(f"Error analyzing contract with Bedrock: {str(e)}")
        # Return default analysis on error
        return {
            'clauses': [],
            'risk_categories': {
                'financial': 5,
                'legal_liability': 5,
                'intellectual_property': 5,
                'termination': 5
            },
            'overall_risk_score': 5,
            'error': str(e)
        }

def format_entities_for_prompt(entities):
    """Format entities into a readable summary for the prompt"""
    if not entities:
        return "No entities detected."
    
    # Group entities by type
    entities_by_type = {}
    for entity in entities:
        entity_type = entity['type']
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity['text'])
    
    # Format as bullet points
    summary_parts = []
    for entity_type, texts in entities_by_type.items():
        unique_texts = list(set(texts))[:5]  # Limit to 5 unique per type
        summary_parts.append(f"- {entity_type}: {', '.join(unique_texts)}")
    
    return "\n".join(summary_parts)

def create_contract_analysis_prompt(text, entity_summary):
    """Create the prompt for Bedrock contract analysis"""
    
    prompt = f"""You are an expert contract analyst specializing in identifying risks for small businesses in India. Analyze the following contract and identify risky clauses.

CONTRACT TEXT:
{text[:15000]}  

DETECTED ENTITIES:
{entity_summary}

ANALYSIS INSTRUCTIONS:
1. Identify all risky clauses in the contract
2. For each risky clause, provide:
   - The clause text (brief excerpt)
   - Risk category (financial, legal_liability, intellectual_property, or termination)
   - Risk score (1-10, where 10 is highest risk)
   - Brief explanation of the risk

3. Focus on these risk patterns:
   - Unfair liability clauses (one-sided indemnification, unlimited liability)
   - Hidden fees or unclear payment terms
   - Restrictive termination clauses (long notice periods, penalties)
   - Intellectual property rights transfers
   - Non-compete or non-solicitation clauses
   - Automatic renewal clauses
   - Jurisdiction issues (non-Indian courts)

4. Consider the Indian Contract Act, 1872 when evaluating risks

RESPONSE FORMAT (JSON):
{{
  "clauses": [
    {{
      "text": "excerpt of risky clause",
      "category": "financial|legal_liability|intellectual_property|termination",
      "risk_score": 1-10,
      "concern": "brief explanation of risk"
    }}
  ]
}}

Provide ONLY the JSON response, no additional text."""

    return prompt

def parse_bedrock_analysis(analysis_text):
    """Parse Claude's JSON response and calculate risk scores"""
    try:
        # Extract JSON from response (Claude sometimes adds markdown formatting)
        json_start = analysis_text.find('{')
        json_end = analysis_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")
        
        json_text = analysis_text[json_start:json_end]
        parsed = json.loads(json_text)
        
        clauses = parsed.get('clauses', [])
        
        # Calculate category scores (average of clause scores in each category)
        category_scores = {
            'financial': [],
            'legal_liability': [],
            'intellectual_property': [],
            'termination': []
        }
        
        for clause in clauses:
            category = clause.get('category', 'legal_liability')
            score = clause.get('risk_score', 5)
            
            if category in category_scores:
                category_scores[category].append(score)
        
        # Calculate averages (default to 0 if no clauses in category)
        risk_categories = {}
        for category, scores in category_scores.items():
            if scores:
                risk_categories[category] = round(sum(scores) / len(scores), 1)
            else:
                risk_categories[category] = 0
        
        # Calculate overall risk score (weighted average)
        # Financial and legal liability are weighted higher
        weights = {
            'financial': 0.35,
            'legal_liability': 0.35,
            'intellectual_property': 0.15,
            'termination': 0.15
        }
        
        overall_score = sum(
            risk_categories[cat] * weights[cat] 
            for cat in weights.keys()
        )
        
        return {
            'clauses': clauses,
            'risk_categories': risk_categories,
            'overall_risk_score': round(overall_score, 1)
        }
        
    except Exception as e:
        print(f"Error parsing Bedrock analysis: {str(e)}")
        print(f"Raw analysis text: {analysis_text[:500]}")
        
        # Return minimal valid structure
        return {
            'clauses': [],
            'risk_categories': {
                'financial': 5,
                'legal_liability': 5,
                'intellectual_property': 5,
                'termination': 5
            },
            'overall_risk_score': 5,
            'parse_error': str(e)
        }

def generate_clause_explanations(clauses):
    """
    Generate plain-language explanations in English and Hindi for each clause.
    Uses Bedrock to create user-friendly explanations.
    """
    clauses_with_explanations = []
    
    for clause in clauses:
        try:
            # Create explanation prompt
            prompt = f"""Explain this contract clause in simple language for a small business owner in India.

CLAUSE: {clause['text']}
RISK: {clause['concern']}

Provide two explanations:
1. ENGLISH: Plain English explanation (2-3 sentences)
2. HINDI: Hindi explanation (2-3 sentences, in Devanagari script)

Focus on what this means for the business and why it's concerning.

RESPONSE FORMAT (JSON):
{{
  "english": "plain English explanation",
  "hindi": "Hindi explanation in Devanagari"
}}

Provide ONLY the JSON response."""

            model_id = "amazon.nova-pro-v1:0"
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 500,
                    "temperature": 0.3
                }
            }
            
            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            explanation_text = response_body['output']['message']['content'][0]['text']
            
            # Parse JSON response
            json_start = explanation_text.find('{')
            json_end = explanation_text.rfind('}') + 1
            if json_start != -1 and json_end > 0:
                explanation_json = json.loads(explanation_text[json_start:json_end])
                clause['explanation_english'] = explanation_json.get('english', '')
                clause['explanation_hindi'] = explanation_json.get('hindi', '')
            else:
                clause['explanation_english'] = 'Explanation not available'
                clause['explanation_hindi'] = 'व्याख्या उपलब्ध नहीं है'
            
            clauses_with_explanations.append(clause)
            
        except Exception as e:
            print(f"Error generating explanation for clause: {str(e)}")
            clause['explanation_english'] = 'Explanation not available'
            clause['explanation_hindi'] = 'व्याख्या उपलब्ध नहीं है'
            clauses_with_explanations.append(clause)
    
    return clauses_with_explanations

def check_indian_contract_act_compliance(text):
    """
    Check contract compliance with Indian Contract Act, 1872.
    Identifies non-compliant clauses and jurisdiction issues.
    """
    try:
        prompt = f"""Analyze this contract for compliance with the Indian Contract Act, 1872.

CONTRACT TEXT (excerpt):
{text[:10000]}

ANALYSIS INSTRUCTIONS:
1. Identify clauses that may violate the Indian Contract Act, 1872
2. Check for jurisdiction issues (non-Indian courts, foreign law)
3. Flag any provisions that may be unenforceable in India

Focus on:
- Section 23: Unlawful consideration or object
- Section 27: Restraint of trade
- Section 28: Restraint of legal proceedings
- Section 16: Undue influence
- Jurisdiction clauses (should be Indian courts)

RESPONSE FORMAT (JSON):
{{
  "issues": [
    {{
      "clause": "brief excerpt of problematic clause",
      "section": "Indian Contract Act section (if applicable)",
      "severity": "high|medium|low",
      "issue": "description of compliance issue",
      "recommendation": "how to address this issue"
    }}
  ]
}}

Provide ONLY the JSON response."""

        model_id = "amazon.nova-pro-v1:0"
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 2000,
                "temperature": 0.3
            }
        }
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        compliance_text = response_body['output']['message']['content'][0]['text']
        
        # Parse JSON response
        json_start = compliance_text.find('{')
        json_end = compliance_text.rfind('}') + 1
        if json_start != -1 and json_end > 0:
            compliance_json = json.loads(compliance_text[json_start:json_end])
            return compliance_json.get('issues', [])
        
        return []
        
    except Exception as e:
        print(f"Error checking compliance: {str(e)}")
        return []

def generate_negotiation_recommendations(clauses):
    """
    Generate negotiation recommendations for high-risk clauses (score >= 7).
    Tailored for small businesses in India.
    """
    high_risk_clauses = [c for c in clauses if c.get('risk_score', 0) >= 7]
    
    if not high_risk_clauses:
        return []
    
    recommendations = []
    
    for clause in high_risk_clauses:
        try:
            prompt = f"""Provide negotiation advice for this high-risk contract clause for a small business in India.

CLAUSE: {clause['text']}
RISK: {clause['concern']}
RISK SCORE: {clause['risk_score']}/10

Provide practical negotiation recommendations:
1. What to ask for (specific changes)
2. Alternative language to propose
3. Fallback position if they won't budge

Keep advice practical and actionable for small business owners.

RESPONSE FORMAT (JSON):
{{
  "recommendation": "main recommendation",
  "alternative_language": "suggested clause wording",
  "fallback": "fallback negotiation position"
}}

Provide ONLY the JSON response."""

            model_id = "amazon.nova-pro-v1:0"
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 600,
                    "temperature": 0.3
                }
            }
            
            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            rec_text = response_body['output']['message']['content'][0]['text']
            
            # Parse JSON response
            json_start = rec_text.find('{')
            json_end = rec_text.rfind('}') + 1
            if json_start != -1 and json_end > 0:
                rec_json = json.loads(rec_text[json_start:json_end])
                recommendations.append({
                    'clause': clause['text'],
                    'category': clause['category'],
                    'risk_score': clause['risk_score'],
                    'recommendation': rec_json.get('recommendation', ''),
                    'alternative_language': rec_json.get('alternative_language', ''),
                    'fallback': rec_json.get('fallback', '')
                })
        
        except Exception as e:
            print(f"Error generating recommendation: {str(e)}")
            continue
    
    return recommendations

def store_analysis_results(contract_id, user_id, extracted_text, entities, clauses, 
                           risk_categories, overall_risk_score, compliance_issues, recommendations):
    """
    Store complete analysis results in DynamoDB Analyses table.
    """
    try:
        import uuid
        
        analysis_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + 'Z'
        
        table = dynamodb.Table(ANALYSES_TABLE)
        
        # Convert floats to Decimal for DynamoDB
        def convert_floats(obj):
            if isinstance(obj, float):
                return Decimal(str(obj))
            elif isinstance(obj, dict):
                return {k: convert_floats(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_floats(item) for item in obj]
            return obj
        
        # Prepare analysis item
        analysis_item = {
            'analysisId': analysis_id,
            'contractId': contract_id,
            'userId': user_id,
            'analyzedAt': now,
            'extractedText': extracted_text[:50000],  # Limit text size for DynamoDB
            'entities': convert_floats(entities),
            'clauses': convert_floats(clauses),
            'riskCategories': convert_floats(risk_categories),
            'overallRiskScore': Decimal(str(overall_risk_score)),
            'complianceIssues': convert_floats(compliance_issues),
            'recommendations': convert_floats(recommendations),
            'status': 'completed'
        }
        
        table.put_item(Item=analysis_item)
        
        return analysis_id
        
    except Exception as e:
        print(f"Error storing analysis results: {str(e)}")
        raise e
