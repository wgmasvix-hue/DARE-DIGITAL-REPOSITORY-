"""Flask application for DARE Research Assistant API"""

import os
import logging
from functools import wraps
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from rosersg.llm import OllamaProvider
from rosersg.dspace import DSpaceClient
from rosersg.rag import RAGEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application"""

    app = Flask(__name__)
    CORS(app)

    # Configuration
    OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    DSPACE_ENDPOINT = os.getenv("DSPACE_ENDPOINT", "https://repo.dare.co.zw")
    API_KEY = os.getenv("ROSERSG_API_KEY", "default-dev-key")

    logger.info(f"Initializing DARE Research Assistant")
    logger.info(f"  Ollama: {OLLAMA_ENDPOINT}")
    logger.info(f"  DSpace: {DSPACE_ENDPOINT}")

    # Initialize components
    llm = OllamaProvider(endpoint=OLLAMA_ENDPOINT, model=OLLAMA_MODEL)
    dspace = DSpaceClient(endpoint=DSPACE_ENDPOINT)
    rag = RAGEngine(llm_provider=llm, dspace_client=dspace)

    # API Key authentication decorator
    def require_api_key(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = request.headers.get("X-API-Key")
            if not key or key != API_KEY:
                return jsonify({"error": "Invalid or missing API key"}), 401
            return f(*args, **kwargs)

        return decorated_function

    # ==================== Health & Status ====================

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint"""
        return jsonify(
            {
                "status": "healthy",
                "service": "rosersg",
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @app.route("/api/status", methods=["GET"])
    def status():
        """Get system status"""
        try:
            ollama_status = "online" if llm.health_check() else "offline"
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            ollama_status = "offline"

        dspace_status = dspace.health_check()

        return jsonify(
            {
                "service": "rosersg",
                "version": "2.0.0",
                "ollama": {"status": ollama_status, "model": OLLAMA_MODEL},
                "dspace": dspace_status,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    # ==================== RAG Chat ====================

    @app.route("/api/chat", methods=["POST"])
    @require_api_key
    def chat():
        """
        Chat endpoint with RAG

        Request body:
        {
            "message": "What is Great Zimbabwe?",
            "query": "..." (alternative to message)
        }
        """
        data = request.json or {}
        question = data.get("message") or data.get("query")

        if not question:
            return jsonify({"error": "Message or query parameter required"}), 400

        logger.info(f"Chat query: {question}")

        try:
            result = rag.query(question)
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return jsonify({"error": str(e), "status": "error"}), 500

    # ==================== Resource-Specific Chat ====================

    @app.route("/api/item/<item_id>/ask", methods=["POST"])
    @require_api_key
    def ask_about_item(item_id):
        """
        Ask a specific question about a DSpace item

        Request body:
        {
            "question": "What methodology was used in this study?"
        }
        """
        data = request.json or {}
        resource_question = data.get("question")

        if not resource_question:
            return jsonify({"error": "Question parameter required"}), 400

        logger.info(f"Item question for {item_id}: {resource_question}")

        try:
            result = rag.ask_about_resource(item_id, resource_question)
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Item question error: {str(e)}")
            return jsonify({"error": str(e), "status": "error"}), 500

    # ==================== Intelligent Search ====================

    @app.route("/api/search/intelligent", methods=["POST"])
    @require_api_key
    def intelligent_search():
        """
        AI-enhanced search

        Request body:
        {
            "query": "Find research about why Great Zimbabwe was abandoned"
        }
        """
        data = request.json or {}
        query = data.get("query")

        if not query:
            return jsonify({"error": "Query parameter required"}), 400

        logger.info(f"Intelligent search: {query}")

        try:
            # Get AI interpretation of query
            interpretation_prompt = f"""Analyze this search query and provide interpretation:
Query: {query}

Provide:
1. Main search concepts (3-5 key terms)
2. Related academic domains
3. Suggested filters

Keep it concise."""

            ai_interpretation = llm.generate(interpretation_prompt)

            # Search DARE
            search_results = dspace.search(query, limit=20)
            items = search_results.get("_embedded", {}).get("searchresources", [])

            # Format results
            formatted_items = rag._format_sources(items)

            return jsonify(
                {
                    "original_query": query,
                    "ai_interpretation": ai_interpretation.strip(),
                    "results": formatted_items,
                    "results_count": len(items),
                    "status": "success",
                }
            )
        except Exception as e:
            logger.error(f"Intelligent search error: {str(e)}")
            return jsonify({"error": str(e), "status": "error"}), 500

    # ==================== Recommendations ====================

    @app.route("/api/recommendations", methods=["POST"])
    @require_api_key
    def get_recommendations():
        """
        Get recommendations based on query or item

        Request body:
        {
            "query": "Great Zimbabwe archaeology"
        } or {
            "item_id": "550e8400-e29b-41d4-a716-446655440000"
        }
        """
        data = request.json or {}
        query = data.get("query")
        item_id = data.get("item_id")

        if not (query or item_id):
            return jsonify({"error": "Query or item_id parameter required"}), 400

        logger.info(f"Recommendations for: {query or item_id}")

        try:
            search_query = query or f"Related to {item_id}"
            search_results = dspace.search(search_query, limit=20)
            items = search_results.get("_embedded", {}).get("searchresources", [])

            # Format as recommendations
            recommendations = rag._format_sources(items[:10])

            return jsonify(
                {
                    "query": search_query,
                    "recommendations": recommendations,
                    "count": len(recommendations),
                    "status": "success",
                }
            )
        except Exception as e:
            logger.error(f"Recommendations error: {str(e)}")
            return jsonify({"error": str(e), "status": "error"}), 500

    # ==================== DSpace Integration ====================

    @app.route("/api/dspace/health", methods=["GET"])
    @require_api_key
    def dspace_health():
        """Check DSpace connection and status"""
        status_info = dspace.health_check()
        http_status = 200 if status_info["status"] == "online" else 503

        return jsonify(
            {
                "dspace": status_info,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ), http_status

    @app.route("/api/dspace/collections", methods=["GET"])
    @require_api_key
    def dspace_collections():
        """Get list of DSpace collections"""
        try:
            collections = dspace.get_collections()
            return jsonify(
                {
                    "collections": collections,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Collections error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    # ==================== Error Handlers ====================

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    debug = os.getenv("DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)
