"""RAG Engine - Core orchestration for grounded AI responses"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval Augmented Generation Engine

    Processes questions through a pipeline:
    1. Search DARE for relevant resources
    2. Retrieve metadata and content
    3. Build context from top results
    4. Generate answer using LLM with context
    5. Format answer with source citations
    """

    def __init__(self, llm_provider, dspace_client, vector_store=None):
        """
        Initialize RAG Engine

        Args:
            llm_provider: LLM provider instance
            dspace_client: DSpace API client instance
            vector_store: Optional vector store for semantic search
        """
        self.llm = llm_provider
        self.dspace = dspace_client
        self.vector_store = vector_store

    def query(self, question: str, max_sources: int = 5) -> Dict[str, Any]:
        """
        Process a question through the RAG pipeline

        Args:
            question: User's question/query
            max_sources: Maximum number of sources to include in context

        Returns:
            Dictionary containing answer and sources
        """
        try:
            # Step 1: Search DARE
            logger.info(f"Searching DARE for: {question}")
            search_results = self.dspace.search(question, limit=10)

            items = search_results.get("_embedded", {}).get("searchresources", [])
            logger.info(f"Found {len(items)} items in DARE")

            if not items:
                return {
                    "response": f"I searched DARE for '{question}' but found no matching resources. "
                    "Please try a different search term.",
                    "sources": [],
                    "search_results_count": 0,
                    "status": "no_results",
                }

            # Step 2: Build context from top results
            context = self._build_context(items[:max_sources])

            # Step 3: Generate answer using LLM
            prompt = self._build_prompt(question, context)
            logger.info("Generating answer with LLM")
            answer = self.llm.generate(prompt)

            # Step 4: Format sources
            sources = self._format_sources(items[:max_sources])

            return {
                "response": answer.strip(),
                "sources": sources,
                "search_results_count": len(items),
                "status": "success",
                "generated_at": datetime.utcnow().isoformat(),
                "context_size": len(context),
            }

        except Exception as e:
            logger.error(f"RAG query error: {str(e)}")
            return {
                "response": f"I encountered an error processing your question: {str(e)}",
                "sources": [],
                "status": "error",
                "error": str(e),
            }

    def _build_context(self, items: List[Dict[str, Any]]) -> str:
        """
        Build context string from DSpace items

        Extracts title, metadata, and other relevant information
        to provide context for the LLM.

        Args:
            items: List of DSpace item objects

        Returns:
            Formatted context string
        """
        context_parts = ["Based on DARE Digital Repository resources:"]

        for i, item in enumerate(items, 1):
            title = item.get("name", "Unknown Title")
            context_parts.append(f"\n{i}. {title}")

            # Extract key metadata
            metadata = item.get("metadata", [])
            for meta in metadata:
                key = meta.get("key", "").replace("dc.", "")
                value = meta.get("value", "")

                # Only include important metadata
                if key in [
                    "title",
                    "creator",
                    "date.issued",
                    "description",
                    "description.abstract",
                    "subject",
                ]:
                    # Clean key name
                    readable_key = key.replace("date.issued", "Date Published").replace(
                        "description.abstract", "Abstract"
                    ).replace("description", "Description").replace("creator", "Author").replace(
                        "subject", "Subject"
                    ).title()

                    context_parts.append(f"  {readable_key}: {value}")

        return "\n".join(context_parts)

    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build the prompt for the LLM

        Combines system message, context, and question
        to guide the LLM to provide grounded answers.

        Args:
            question: User's question
            context: Background context from DARE resources

        Returns:
            Full prompt for the LLM
        """
        return f"""You are DARE Research Assistant, powered by ChengetAI.
Your role is to help researchers understand research in the DARE Digital Repository.

You have been provided with relevant resources from DARE to answer the following question.
Base your answer ONLY on the provided resources.
If the resources don't contain sufficient information, say so clearly.
NEVER fabricate or invent citations, sources, or facts.
NEVER attribute information to a resource unless it clearly appears in the provided context.

{context}

Question: {question}

Answer based only on the DARE resources provided above. If DARE resources are insufficient to answer the question, say so clearly."""

    def _format_sources(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format search results as proper citations

        Args:
            items: List of DSpace items

        Returns:
            List of formatted source citations
        """
        sources = []

        for item in items:
            uuid = item.get("uuid", "")
            if not uuid:
                continue

            source = {
                "uuid": uuid,
                "title": item.get("name", "Unknown"),
                "url": f"https://repo.dare.co.zw/items/{uuid}",
                "date": None,
                "authors": [],
                "subjects": [],
                "description": None,
            }

            # Extract metadata
            for meta in item.get("metadata", []):
                key = meta.get("key", "")
                value = meta.get("value", "")

                if key == "dc.date.issued":
                    source["date"] = value
                elif key == "dc.creator":
                    if value not in source["authors"]:
                        source["authors"].append(value)
                elif key == "dc.subject":
                    if value not in source["subjects"]:
                        source["subjects"].append(value)
                elif key in ["dc.description", "dc.description.abstract"]:
                    if not source["description"]:
                        source["description"] = value[:200] + (
                            "..." if len(value) > 200 else ""
                        )

            sources.append(source)

        return sources

    def ask_about_resource(
        self, item_uuid: str, resource_question: str
    ) -> Dict[str, Any]:
        """
        Ask a specific question about a particular resource

        Args:
            item_uuid: UUID of the DSpace item
            resource_question: Question about the resource

        Returns:
            Dictionary with answer about the resource
        """
        try:
            # Get the specific item
            item = self.dspace.get_item(item_uuid)

            if "error" in item:
                return {
                    "response": f"Could not find item {item_uuid}",
                    "status": "error",
                }

            # Build context from just this item
            context = self._build_context([item])

            # Ask question about this specific resource
            prompt = f"""You are DARE Research Assistant analyzing a specific research item.

{context}

Question about this resource: {resource_question}

Answer based only on the information in this resource. If the resource doesn't contain information about the question, say so."""

            answer = self.llm.generate(prompt)

            # Return answer with the source
            return {
                "response": answer.strip(),
                "source": self._format_sources([item])[0] if item else None,
                "status": "success",
            }

        except Exception as e:
            logger.error(f"Error asking about resource: {str(e)}")
            return {
                "response": f"Error processing request: {str(e)}",
                "status": "error",
            }
