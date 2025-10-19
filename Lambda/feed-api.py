import json
import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('NewsArticles')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    query_params = event.get('queryStringParameters') or {}
    user_region = query_params.get('region', 'north-america')
    user_category = query_params.get('category', 'technology')
    limit = int(query_params.get('limit', '10'))
    
    try:
        filter_expression = Attr('region').eq(user_region) & Attr('category').eq(user_category)
        response = table.scan(FilterExpression=filter_expression, Limit=20)
        articles = response.get('Items', [])
        articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        articles = articles[:limit]
        
        for i, article in enumerate(articles):
            article['relevance_score'] = round(1.0 - (i * 0.05), 2)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'count': len(articles),
                'preferences': {'region': user_region, 'category': user_category},
                'feed': articles
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }