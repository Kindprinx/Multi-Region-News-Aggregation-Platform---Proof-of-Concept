import json
import boto3
import urllib3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('NewsArticles')
http = urllib3.PoolManager()

def lambda_handler(event, context):
    api_key = 'YOUR_NEWSAPI_KEY_HERE'  # Replace with your key
    url = f'https://newsapi.org/v2/top-headlines?country=us&category=technology&pageSize=10&apiKey={api_key}'
    
    try:
        response = http.request('GET', url)
        data = json.loads(response.data.decode('utf-8'))
        articles = data.get('articles', [])
        
        ingested_count = 0
        for article in articles:
            if article.get('title') == '[Removed]':
                continue
                
            table.put_item(Item={
                'article_id': str(uuid.uuid4()),
                'title': article.get('title', 'No title'),
                'description': article.get('description', 'No description'),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'published_at': article.get('publishedAt', datetime.now().isoformat()),
                'image_url': article.get('urlToImage', ''),
                'region': 'north-america',
                'category': 'technology',
                'ingested_at': datetime.now().isoformat()
            })
            ingested_count += 1
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully ingested {ingested_count} articles')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }