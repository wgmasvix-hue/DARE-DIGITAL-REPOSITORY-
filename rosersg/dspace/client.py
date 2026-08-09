"""DSpace REST API Client for accessing digital repository"""

import os
import logging
import requests
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


class DSpaceClient:
    """Client for interacting with DSpace REST API"""

    def __init__(self, endpoint: str, api_token: Optional[str] = None):
        """
        Initialize DSpace client

        Args:
            endpoint: DSpace base URL (e.g., https://repo.dare.co.zw)
            api_token: Optional JWT token for authentication
        """
        self.endpoint = endpoint
        self.api_url = f"{endpoint}/server/api"
        self.api_token = api_token or os.getenv("DSPACE_API_TOKEN")
        self.headers = self._build_headers()

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with optional authentication"""
        headers = {"Accept": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def search(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0,
        dso_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search DSpace items with optional type filter

        Args:
            query: Search query string
            limit: Maximum results to return
            offset: Pagination offset
            dso_type: Optional DSpace Object type filter (e.g., 'item', 'collection')

        Returns:
            JSON response with search results
        """
        try:
            url = f"{self.api_url}/discover/search"
            params = {"query": query, "limit": limit, "offset": offset}

            if dso_type:
                params["dsoType"] = dso_type

            response = requests.get(
                url, params=params, headers=self.headers, timeout=30, verify=True
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace search error: {str(e)}")
            return {"error": f"DSpace search failed: {str(e)}", "status": "error"}

    def get_item(self, item_id: str) -> Dict[str, Any]:
        """
        Get specific DSpace item with all metadata

        Args:
            item_id: UUID of the item

        Returns:
            JSON response with item details
        """
        try:
            url = f"{self.api_url}/core/items/{item_id}"
            response = requests.get(
                url, headers=self.headers, timeout=30, verify=True
            )
            response.raise_for_status()
            item = response.json()

            # Get bitstreams if available
            if "uuid" in item:
                item["bitstreams"] = self._get_bitstreams(item["uuid"])

            return item

        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace get item error: {str(e)}")
            return {"error": f"Item not found: {str(e)}", "status": "error"}

    def _get_bitstreams(self, item_uuid: str) -> Dict[str, Any]:
        """
        Get bitstreams (files) associated with an item

        Args:
            item_uuid: UUID of the item

        Returns:
            JSON response with bitstream information
        """
        try:
            url = f"{self.api_url}/core/items/{item_uuid}/bitstreams"
            response = requests.get(
                url, headers=self.headers, timeout=30, verify=True
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Could not retrieve bitstreams: {e}")
            return {"error": "Could not retrieve bitstreams"}

    def get_collections(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get all DSpace collections

        Args:
            limit: Maximum collections to return

        Returns:
            JSON response with collections
        """
        try:
            url = f"{self.api_url}/core/collections"
            params = {"limit": limit}
            response = requests.get(
                url, params=params, headers=self.headers, timeout=30, verify=True
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace collections error: {str(e)}")
            return {"error": str(e), "status": "error"}

    def get_collection_items(self, collection_id: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get items in a specific collection

        Args:
            collection_id: UUID of the collection
            limit: Maximum items to return

        Returns:
            JSON response with items in collection
        """
        try:
            url = f"{self.api_url}/core/collections/{collection_id}/items"
            params = {"limit": limit}
            response = requests.get(
                url, params=params, headers=self.headers, timeout=30, verify=True
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace get collection items error: {str(e)}")
            return {"error": str(e), "status": "error"}

    def get_metadata_fields(self) -> Dict[str, Any]:
        """
        Get available metadata fields in DSpace

        Returns:
            JSON response with metadata field definitions
        """
        try:
            url = f"{self.api_url}/core/metadatafields"
            response = requests.get(
                url, headers=self.headers, timeout=30, verify=True
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"DSpace metadata fields error: {str(e)}")
            return {"error": str(e), "status": "error"}

    def health_check(self) -> Dict[str, Any]:
        """
        Check if DSpace is accessible and healthy

        Returns:
            Dictionary with status information
        """
        try:
            response = requests.get(
                f"{self.api_url}/discover/search",
                headers=self.headers,
                timeout=10,
                verify=True,
            )
            return {
                "status": "online" if response.status_code == 200 else "error",
                "endpoint": self.endpoint,
                "authenticated": bool(self.api_token),
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"DSpace health check failed: {e}")
            return {
                "status": "offline",
                "endpoint": self.endpoint,
                "authenticated": bool(self.api_token),
            }
