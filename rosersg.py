#!/usr/bin/env python3
"""
rosersg - Ollama-powered AI assistant for DSpace Digital Repository
Provides intelligent search, metadata optimization, recommendations, and conversational AI
"""

import os
import json
import logging
import requests
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open('rosersg-config.json', 'r') as f:
    CONFIG = json.load(f)

OLLAMA_ENDPOINT = os.getenv('OLLAMA_ENDPOINT', CONFIG['ollama']['endpoint'])
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', CONFIG['ollama']['model'])
DSPACE_ENDPOINT = os.getenv('DSPACE_ENDPOINT', CONFIG['dspace']['endpoint'])
API_KEY = os.getenv('ROSERSG_API_KEY', 'default-dev-key')


class OllamaClient:
    def __init__(self, endpoint, model):
        self.endpoint = endpoint
        self.model = model

    def generate(self, prompt, stream=False):
        """Generate text using Ollama"""
        try:
            url = f"{self.endpoint}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "temperature": CONFIG['ollama']['temperature']
            }
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()

            if stream:
                return response.iter_lines()
            else:
                result = response.json()
                return result.get('response', '')
        except Exception as e:
            logger.error(f"Ollama generation error: {str(e)}")
            raise

    def embed(self, text):
        """Generate embeddings for text"""
        try:
            url = f"{self.endpoint}/api/embed"
            payload = {
                "model": "nomic-embed-text",
                "input": text
            }
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get('embeddings', [])
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise


class DSpaceClient:
    def __init__(self, endpoint, api_token=None):
        self.endpoint = endpoint
        self.api_url = f"{endpoint}/server/api"
        self.api_token = api_token or os.getenv('DSPACE_API_TOKEN')
        self.headers = self._build_headers()

    def _build_headers(self):
        """Build headers with optional authentication"""
        headers = {"Accept": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def search(self, query, limit=50, dso_type=None):
        """Search DSpace items with optional type filter"""
        try:
            url = f"{self.api_url}/discover/search"
            params = {
                "query": query,
                "limit": limit,
                "offset": 0
            }
            if dso_type:
                params["dsoType"] = dso_type

            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=30,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace search error: {str(e)}")
            return {"error": f"DSpace search failed: {str(e)}", "status": "error"}

    def get_item(self, item_id):
        """Get specific DSpace item with all metadata"""
        try:
            url = f"{self.api_url}/core/items/{item_id}"
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30,
                verify=True
            )
            response.raise_for_status()
            item = response.json()

            # Get bitstreams if needed
            if "uuid" in item:
                item["bitstreams"] = self._get_bitstreams(item["uuid"])

            return item
        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace get item error: {str(e)}")
            return {"error": f"Item not found: {str(e)}", "status": "error"}

    def _get_bitstreams(self, item_uuid):
        """Get bitstreams for an item"""
        try:
            url = f"{self.api_url}/core/items/{item_uuid}/bitstreams"
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except:
            return {"error": "Could not retrieve bitstreams"}

    def get_collections(self, limit=50):
        """Get all DSpace collections"""
        try:
            url = f"{self.api_url}/core/collections"
            params = {"limit": limit}
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=30,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace collections error: {str(e)}")
            return {"error": str(e), "status": "error"}

    def get_collection_items(self, collection_id, limit=50):
        """Get items in a specific collection"""
        try:
            url = f"{self.api_url}/core/collections/{collection_id}/items"
            params = {"limit": limit}
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=30,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace get collection items error: {str(e)}")
            return {"error": str(e), "status": "error"}

    def get_metadata_fields(self):
        """Get available metadata fields in DSpace"""
        try:
            url = f"{self.api_url}/core/metadatafields"
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace metadata fields error: {str(e)}")
            return {"error": str(e), "status": "error"}

    def health_check(self):
        """Check if DSpace is accessible"""
        try:
            response = requests.get(
                f"{self.api_url}/discover/search",
                headers=self.headers,
                timeout=10,
                verify=True
            )
            return {
                "status": "online" if response.status_code == 200 else "error",
                "endpoint": self.endpoint,
                "authenticated": bool(self.api_token)
            }
        except requests.exceptions.RequestException:
            return {
                "status": "offline",
                "endpoint": self.endpoint,
                "authenticated": bool(self.api_token)
            }


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if not key or key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function


ollama = OllamaClient(OLLAMA_ENDPOINT, OLLAMA_MODEL)
dspace = DSpaceClient(DSPACE_ENDPOINT)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "rosersg",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/chat', methods=['POST'])
@require_api_key
def chat():
    """Interactive chat with rosersg AI"""
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Message required"}), 400

    try:
        system_prompt = """You are rosersg, an intelligent AI assistant for the DARE Digital Repository powered by DSpace.
Your role is to help users discover, understand, and interact with academic research and digital collections.
Be helpful, accurate, and conversational. When users ask about the repository, provide useful information.
When you don't know something, say so clearly."""

        full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
        response_text = ollama.generate(full_prompt)

        return jsonify({
            "message": user_message,
            "response": response_text.strip(),
            "model": OLLAMA_MODEL,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/search/intelligent', methods=['POST'])
@require_api_key
def intelligent_search():
    """AI-enhanced semantic search"""
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"error": "Query required"}), 400

    try:
        ai_prompt = f"""Analyze this search query and suggest improved search terms for finding academic research:
Query: {query}

Provide:
1. Refined search terms (3-5 variations)
2. Relevant academic domains
3. Recommended filters

Keep it concise and structured."""

        enhanced_query = ollama.generate(ai_prompt)
        search_results = dspace.search(query)

        return jsonify({
            "original_query": query,
            "ai_suggestions": enhanced_query.strip(),
            "search_results": search_results,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Intelligent search error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/metadata/optimize', methods=['POST'])
@require_api_key
def optimize_metadata():
    """Suggest metadata improvements using AI"""
    data = request.json
    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({"error": "Title required"}), 400

    try:
        prompt = f"""As a metadata specialist, improve the following academic item metadata:

Title: {title}
Description: {description or 'Not provided'}

Suggest improvements for:
1. More descriptive keywords
2. Subject classifications
3. Enhanced title if needed
4. Better description

Be specific and practical."""

        suggestions = ollama.generate(prompt)

        return jsonify({
            "original_title": title,
            "original_description": description,
            "ai_suggestions": suggestions.strip(),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Metadata optimization error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/item/<item_id>/summarize', methods=['GET'])
@require_api_key
def summarize_item(item_id):
    """Generate AI summary of a DSpace item"""
    try:
        item = dspace.get_item(item_id)

        if "error" in item:
            return jsonify(item), 404

        content = f"Title: {item.get('name', 'N/A')}\n"
        if 'metadata' in item:
            for meta in item.get('metadata', []):
                content += f"{meta.get('key', 'N/A')}: {meta.get('value', 'N/A')}\n"

        prompt = f"""Summarize this academic item in 2-3 sentences for a researcher:

{content}

Make it informative and engaging."""

        summary = ollama.generate(prompt)

        return jsonify({
            "item_id": item_id,
            "item_title": item.get('name'),
            "ai_summary": summary.strip(),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Item summarization error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/recommendations', methods=['POST'])
@require_api_key
def get_recommendations():
    """Get AI-powered item recommendations"""
    data = request.json
    query = data.get('query')
    item_id = data.get('item_id')

    if not (query or item_id):
        return jsonify({"error": "Query or item_id required"}), 400

    try:
        search_query = query or f"Related to item {item_id}"
        results = dspace.search(search_query, limit=20)

        prompt = f"""Based on this research topic, rank these items by relevance and explain why:

Topic: {search_query}

Analyze the search results and provide recommendations."""

        analysis = ollama.generate(prompt)

        return jsonify({
            "query": search_query,
            "recommendations": analysis.strip(),
            "search_results": results,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Recommendations error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/collections/insights', methods=['GET'])
@require_api_key
def collection_insights():
    """Generate insights about DSpace collections"""
    try:
        collections = dspace.get_collections()

        if "error" in collections:
            return jsonify(collections), 500

        prompt = f"""Analyze these academic collections and provide insights:

Collections data: {json.dumps(collections)[:1000]}...

Provide:
1. Collection overview
2. Content patterns
3. Recommended improvements
4. Engagement opportunities"""

        insights = ollama.generate(prompt)

        return jsonify({
            "collections": collections,
            "ai_insights": insights.strip(),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Collection insights error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Get rosersg system status"""
    try:
        ollama_response = requests.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=5)
        ollama_status = "online" if ollama_response.status_code == 200 else "offline"
    except:
        ollama_status = "offline"

    dspace_status = dspace.health_check()

    return jsonify({
        "service": "rosersg",
        "version": "1.0.0",
        "features": CONFIG['rosersg_features'],
        "ollama_status": ollama_status,
        "dspace": dspace_status,
        "dspace_endpoint": DSPACE_ENDPOINT,
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/dspace/health', methods=['GET'])
@require_api_key
def dspace_health():
    """Check DSpace connection and status"""
    status = dspace.health_check()
    http_status = 200 if status["status"] == "online" else 503

    return jsonify({
        "dspace_status": status,
        "timestamp": datetime.utcnow().isoformat()
    }), http_status


@app.route('/api/dspace/collections', methods=['GET'])
@require_api_key
def dspace_collections_list():
    """Get list of DSpace collections"""
    try:
        collections = dspace.get_collections()
        return jsonify({
            "collections": collections,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Collections list error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/dspace/collection/<collection_id>/items', methods=['GET'])
@require_api_key
def dspace_collection_items(collection_id):
    """Get items in a specific collection"""
    try:
        limit = request.args.get('limit', 50, type=int)
        items = dspace.get_collection_items(collection_id, limit)
        return jsonify({
            "items": items,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Collection items error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/dspace/metadata-fields', methods=['GET'])
@require_api_key
def dspace_metadata_fields():
    """Get available DSpace metadata fields"""
    try:
        fields = dspace.get_metadata_fields()
        return jsonify({
            "metadata_fields": fields,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Metadata fields error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug)
