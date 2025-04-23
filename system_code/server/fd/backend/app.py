import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime
import re
import psycopg2

# Add parent directory to path to import from system_code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from system_code.server.database.postgres_client import PGClient
from system_code.core.rag_sdk import RagSdk
from system_code.core.config import Config

app = Flask(__name__)
CORS(app)

# Initialize database client
db_client = PGClient()

# Initialize RAG system
config = Config()
rag = RagSdk()


@app.route('/api/search', methods=['POST'])
def search():
    """Standard search endpoint"""
    try:
        data = request.get_json()
        query = data.get('query')
        limit = data.get('limit', 10)
        
        results = rag.search(query, limit)
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/deep_search', methods=['POST'])
def deep_search():
    """Deep search endpoint with enhanced parameters"""
    try:
        data = request.get_json()
        query = data.get('query')
        limit = data.get('limit', 10)
        
        # Use deep search method for enhanced search
        results = rag.deep_search(
            query,
            limit
        )
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/bot_rate', methods=['GET'])
def get_bot_rate():
    """Get bot rate by date"""
    try:
        # Get date range from query parameters
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Build query with filters
        query = """
            SELECT 
                TO_CHAR(TO_TIMESTAMP(timestamp / 1000), 'YYYY-MM-DD') as date,
                COUNT(*) as total_reviews,
                SUM(CASE WHEN real_review = FALSE THEN 1 ELSE 0 END) as bot_reviews,
                ROUND(CAST((SUM(CASE WHEN real_review = FALSE THEN 1 ELSE 0 END)::float / COUNT(*)) * 100 AS numeric), 2) as bot_rate
            FROM beauty_reviews
            WHERE 1=1
        """
        
        params = []
        
        # Add date filters if provided
        if start_date:
            query += " AND timestamp >= extract(epoch from to_timestamp(%s, 'YYYY-MM-DD')) * 1000"
            params.append(start_date)
        
        if end_date:
            # Add 86399999 milliseconds (23:59:59.999) to include the entire end date
            query += " AND timestamp <= extract(epoch from to_timestamp(%s, 'YYYY-MM-DD')) * 1000 + 86399999"
            params.append(end_date)
        
        # Add filter for real_reviews if provided
        real_reviews = request.args.get('real_reviews', None)
        if real_reviews is not None:
            real_reviews_bool = real_reviews.lower() == 'true'
            query += " AND real_review = %s"
            params.append(real_reviews_bool)
        
        # Add filter for sentiment if provided
        sentiment = request.args.get('sentiment', None)
        if sentiment:
            query += " AND sentiment = %s"
            params.append(sentiment)
        
        # Group by date and order by date
        query += """
            GROUP BY TO_CHAR(TO_TIMESTAMP(timestamp / 1000), 'YYYY-MM-DD')
            ORDER BY date
        """
        
        try:
            # Execute query
            results = db_client.execute(query, params)
            
            # Format results
            data = [{
                'date': row[0],
                'total_reviews': row[1],
                'bot_reviews': row[2],
                'bot_rate': row[3]
            } for row in results]
            
            return jsonify({
                'success': True,
                'data': data
            })
        except psycopg2.Error as db_err:
            # 特别处理PostgreSQL错误
            return jsonify({
                'success': False,
                'error': f'数据库错误: {str(db_err)}',
                'error_code': db_err.pgcode if hasattr(db_err, 'pgcode') else 'UNKNOWN'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/sentiment', methods=['GET'])
def get_sentiment_distribution():
    """Get sentiment distribution"""
    try:
        # Get date range from query parameters
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Build query with filters
        query = """
            SELECT 
                sentiment,
                COUNT(*) as count
            FROM beauty_reviews
            WHERE sentiment != ''
        """
        
        params = []
        
        # Add date filters if provided
        if start_date:
            query += " AND timestamp >= extract(epoch from to_timestamp(%s, 'YYYY-MM-DD')) * 1000"
            params.append(start_date)
        
        if end_date:
            # Add 86399999 milliseconds (23:59:59.999) to include the entire end date
            query += " AND timestamp <= extract(epoch from to_timestamp(%s, 'YYYY-MM-DD')) * 1000 + 86399999"
            params.append(end_date)
        
        # Add filter for real_reviews if provided
        real_reviews = request.args.get('real_reviews', None)
        if real_reviews is not None:
            real_reviews_bool = real_reviews.lower() == 'true'
            query += " AND real_review = %s"
            params.append(real_reviews_bool)
        
        # Group by sentiment
        query += """
            GROUP BY sentiment
            ORDER BY count DESC
        """
        
        try:
            # Execute query
            results = db_client.execute(query, params)
            
            # Format results
            data = [{
                'sentiment': row[0],
                'count': row[1]
            } for row in results]
            
            return jsonify({
                'success': True,
                'data': data
            })
        except psycopg2.Error as db_err:
            # 特别处理PostgreSQL错误
            return jsonify({
                'success': False,
                'error': f'数据库错误: {str(db_err)}',
                'error_code': db_err.pgcode if hasattr(db_err, 'pgcode') else 'UNKNOWN'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/wordcloud', methods=['GET'])
def get_wordcloud_data():
    """Get word frequency for wordcloud"""
    try:
        # Get date range from query parameters
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Build query with filters
        query = """
            SELECT text
            FROM beauty_reviews
            WHERE text != ''
        """
        
        params = []
        
        # Add date filters if provided
        if start_date:
            query += " AND timestamp >= extract(epoch from to_timestamp(%s, 'YYYY-MM-DD')) * 1000"
            params.append(start_date)
        
        if end_date:
            # Add 86399999 milliseconds (23:59:59.999) to include the entire end date
            query += " AND timestamp <= extract(epoch from to_timestamp(%s, 'YYYY-MM-DD')) * 1000 + 86399999"
            params.append(end_date)
        
        # Add filter for real_reviews if provided
        real_reviews = request.args.get('real_reviews', None)
        if real_reviews is not None:
            real_reviews_bool = real_reviews.lower() == 'true'
            query += " AND real_review = %s"
            params.append(real_reviews_bool)
        
        # Add filter for sentiment if provided
        sentiment = request.args.get('sentiment', None)
        if sentiment:
            query += " AND sentiment = %s"
            params.append(sentiment)
        
        try:
            # Execute query
            results = db_client.execute(query, params)
            
            # Process text to get word frequencies
            all_text = ' '.join([row[0] for row in results])
            
            # Remove common stop words (English)
            stop_words = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
                'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
                'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
                'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
                'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
                'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
            }
            
            # Clean text and count word frequencies
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            word_freq = {}
            
            for word in words:
                if word not in stop_words:
                    if word in word_freq:
                        word_freq[word] += 1
                    else:
                        word_freq[word] = 1
            
            # Convert to list of objects for the frontend
            data = [{'text': word, 'value': count} for word, count in word_freq.items()]
            
            # Sort by frequency and limit to top 100 words
            data.sort(key=lambda x: x['value'], reverse=True)
            data = data[:100]
            
            return jsonify({
                'success': True,
                'data': data
            })
        except psycopg2.Error as db_err:
            # 特别处理PostgreSQL错误
            return jsonify({
                'success': False,
                'error': f'数据库错误: {str(db_err)}',
                'error_code': db_err.pgcode if hasattr(db_err, 'pgcode') else 'UNKNOWN'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/review_trend', methods=['GET'])
def get_review_trend():
    """Get review count trend by date"""
    try:
        # Get date range from query parameters
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Build query with filters
        query = """
            SELECT 
                TO_CHAR(TO_TIMESTAMP(timestamp / 1000), 'YYYY-MM-DD') as date,
                COUNT(*) as review_count
            FROM beauty_reviews
            WHERE 1=1
        """
        
        params = []
        
        # Add date filters if provided
        if start_date:
            query += " AND timestamp >= extract(epoch from to_timestamp(%s, 'YYYY-MM-DD')) * 1000"
            params.append(start_date)
        
        if end_date:
            # Add 86399999 milliseconds (23:59:59.999) to include the entire end date
            query += " AND timestamp <= extract(epoch from to_timestamp(%s, 'YYYY-MM-DD')) * 1000 + 86399999"
            params.append(end_date)
        
        # Add filter for real_reviews if provided
        real_reviews = request.args.get('real_reviews', None)
        if real_reviews is not None:
            real_reviews_bool = real_reviews.lower() == 'true'
            query += " AND real_review = %s"
            params.append(real_reviews_bool)
        
        # Add filter for sentiment if provided
        sentiment = request.args.get('sentiment', None)
        if sentiment:
            query += " AND sentiment = %s"
            params.append(sentiment)
        
        # Group by date and order by date
        query += """
            GROUP BY TO_CHAR(TO_TIMESTAMP(timestamp / 1000), 'YYYY-MM-DD')
            ORDER BY date
        """
        
        try:
            # Execute query
            results = db_client.execute(query, params)
            
            # Format results
            data = [{
                'date': row[0],
                'review_count': row[1]
            } for row in results]
            
            return jsonify({
                'success': True,
                'data': data
            })
        except psycopg2.Error as db_err:
            # 特别处理PostgreSQL错误
            return jsonify({
                'success': False,
                'error': f'数据库错误: {str(db_err)}',
                'error_code': db_err.pgcode if hasattr(db_err, 'pgcode') else 'UNKNOWN'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)