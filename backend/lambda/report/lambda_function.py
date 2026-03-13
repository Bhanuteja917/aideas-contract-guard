import json
import boto3
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

ANALYSES_TABLE = os.environ['ANALYSES_TABLE']
REPORTS_BUCKET = os.environ['REPORTS_BUCKET']

def lambda_handler(event, context):
    print(f"Report Lambda invoked: {json.dumps(event)}")
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
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
        
        # Get contractId from path parameters
        contract_id = event.get('pathParameters', {}).get('contractId')
        if not contract_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'contractId is required'})
            }
        
        # Fetch analysis from DynamoDB
        table = dynamodb.Table(ANALYSES_TABLE)
        response = table.query(
            IndexName='contractId-index',
            KeyConditionExpression='contractId = :cid',
            ExpressionAttributeValues={':cid': contract_id},
            Limit=1
        )
        
        if not response.get('Items'):
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Analysis not found'})
            }
        
        analysis = response['Items'][0]
        
        # Verify user owns this analysis
        if analysis.get('userId') != user_id:
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({'error': 'Access denied'})
            }
        
        # Generate PDF report
        pdf_buffer = generate_pdf_report(analysis, contract_id)
        
        # Upload to S3
        report_key = f"{user_id}/{contract_id}_report.pdf"
        s3_client.put_object(
            Bucket=REPORTS_BUCKET,
            Key=report_key,
            Body=pdf_buffer.getvalue(),
            ContentType='application/pdf'
        )
        
        # Generate pre-signed download URL (15 minutes)
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': REPORTS_BUCKET,
                'Key': report_key
            },
            ExpiresIn=900
        )
        
        print(f"Generated report for contract {contract_id}")
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'downloadUrl': download_url,
                'reportKey': report_key
            })
        }
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def generate_pdf_report(analysis, contract_id):
    """Generate PDF report from analysis data"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Title
    elements.append(Paragraph("ContractGuard Analysis Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Contract Info
    elements.append(Paragraph(f"<b>Contract ID:</b> {contract_id}", styles['Normal']))
    elements.append(Paragraph(f"<b>Analysis Date:</b> {analysis.get('analyzedAt', 'N/A')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Overall Risk Score
    overall_score = float(analysis.get('overallRiskScore', 0))
    risk_level = get_risk_level(overall_score)
    risk_color = get_risk_color_hex(overall_score)
    
    elements.append(Paragraph("Overall Risk Assessment", heading_style))
    
    risk_data = [
        ['Risk Score', 'Risk Level'],
        [f'{overall_score:.1f} / 10', risk_level]
    ]
    
    risk_table = Table(risk_data, colWidths=[2*inch, 3*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor(risk_color)),
    ]))
    
    elements.append(risk_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Risk Categories
    elements.append(Paragraph("Risk by Category", heading_style))
    
    risk_categories = analysis.get('riskCategories', {})
    category_data = [['Category', 'Score', 'Level']]
    
    for category, score in risk_categories.items():
        score_float = float(score)
        category_name = category.replace('_', ' ').title()
        level = get_risk_level(score_float)
        category_data.append([category_name, f'{score_float:.1f}', level])
    
    category_table = Table(category_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
    category_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(category_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Identified Risks
    clauses = analysis.get('clauses', [])
    if clauses:
        elements.append(Paragraph(f"Identified Risks ({len(clauses)} found)", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        for i, clause in enumerate(clauses, 1):
            risk_score = float(clause.get('risk_score', 0))
            category = clause.get('category', '').replace('_', ' ').title()
            concern = clause.get('concern', '')
            clause_text = clause.get('text', '')
            explanation_english = clause.get('explanation_english', '')
            
            # Risk header with score
            risk_header = f"<b>Risk #{i}: {category}</b> - Score: {risk_score:.1f}/10"
            elements.append(Paragraph(risk_header, styles['Normal']))
            elements.append(Spacer(1, 0.05*inch))
            
            # Clause text
            if clause_text:
                elements.append(Paragraph("<b>Clause Text:</b>", styles['Normal']))
                # Limit clause text to 500 characters for readability
                display_text = clause_text[:500] + ('...' if len(clause_text) > 500 else '')
                elements.append(Paragraph(f'<i>"{display_text}"</i>', styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
            
            # Concern
            if concern:
                elements.append(Paragraph(f"<b>Concern:</b> {concern}", styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
            
            # Plain-language explanation
            if explanation_english:
                elements.append(Paragraph("<b>Explanation:</b>", styles['Normal']))
                elements.append(Paragraph(explanation_english, styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
            
            # Add separator between risks
            elements.append(Spacer(1, 0.15*inch))
            if i < len(clauses):
                elements.append(Paragraph("_" * 80, styles['Normal']))
                elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Compliance Issues
    compliance_issues = analysis.get('complianceIssues', [])
    if compliance_issues:
        elements.append(Paragraph(f"Compliance Issues ({len(compliance_issues)} found)", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        for i, issue in enumerate(compliance_issues, 1):
            severity = issue.get('severity', 'medium').upper()
            issue_text = issue.get('issue', '')
            clause_text = issue.get('clause', '')
            section = issue.get('section', '')
            recommendation = issue.get('recommendation', '')
            
            # Issue header
            header = f"<b>Issue #{i}</b> - Severity: {severity}"
            if section:
                header += f" ({section})"
            elements.append(Paragraph(header, styles['Normal']))
            elements.append(Spacer(1, 0.05*inch))
            
            # Clause text
            if clause_text:
                elements.append(Paragraph("<b>Clause:</b>", styles['Normal']))
                display_text = clause_text[:300] + ('...' if len(clause_text) > 300 else '')
                elements.append(Paragraph(f'<i>"{display_text}"</i>', styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
            
            # Issue description
            if issue_text:
                elements.append(Paragraph(f"<b>Issue:</b> {issue_text}", styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
            
            # Recommendation
            if recommendation:
                elements.append(Paragraph(f"<b>Recommendation:</b> {recommendation}", styles['Normal']))
            
            # Add separator
            elements.append(Spacer(1, 0.15*inch))
            if i < len(compliance_issues):
                elements.append(Paragraph("_" * 80, styles['Normal']))
                elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Negotiation Recommendations
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        elements.append(Paragraph(f"Negotiation Recommendations ({len(recommendations)} provided)", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        for i, rec in enumerate(recommendations, 1):
            category = rec.get('category', '').replace('_', ' ').title()
            risk_score = rec.get('risk_score', 0)
            clause_text = rec.get('clause', '')
            recommendation = rec.get('recommendation', '')
            alternative_language = rec.get('alternative_language', '')
            fallback = rec.get('fallback', '')
            
            # Recommendation header
            elements.append(Paragraph(
                f"<b>Recommendation #{i}: {category}</b> (Risk Score: {risk_score}/10)",
                styles['Normal']
            ))
            elements.append(Spacer(1, 0.05*inch))
            
            # Original clause
            if clause_text:
                elements.append(Paragraph("<b>Original Clause:</b>", styles['Normal']))
                display_text = clause_text[:300] + ('...' if len(clause_text) > 300 else '')
                elements.append(Paragraph(f'<i>"{display_text}"</i>', styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
            
            # Main recommendation
            if recommendation:
                elements.append(Paragraph("<b>What to Negotiate:</b>", styles['Normal']))
                elements.append(Paragraph(recommendation, styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
            
            # Alternative language
            if alternative_language:
                elements.append(Paragraph("<b>Suggested Alternative Language:</b>", styles['Normal']))
                elements.append(Paragraph(f'<i>"{alternative_language}"</i>', styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))
            
            # Fallback position
            if fallback:
                elements.append(Paragraph("<b>Fallback Position:</b>", styles['Normal']))
                elements.append(Paragraph(fallback, styles['Normal']))
            
            # Add separator
            elements.append(Spacer(1, 0.15*inch))
            if i < len(recommendations):
                elements.append(Paragraph("_" * 80, styles['Normal']))
                elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "<i>This report was generated by ContractGuard AI. "
        "Please consult with a legal professional for specific advice.</i>",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

def get_risk_level(score):
    """Get risk level label from score"""
    if score <= 3:
        return 'Low Risk'
    elif score <= 6:
        return 'Medium Risk'
    else:
        return 'High Risk'

def get_risk_color_hex(score):
    """Get hex color for risk score"""
    if score <= 3:
        return '#16a34a'  # green
    elif score <= 6:
        return '#ca8a04'  # yellow
    else:
        return '#dc2626'  # red
