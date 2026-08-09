#!/usr/bin/env python3
"""
Phase 1 Test Suite - Validate RAG Core Implementation

Tests RAG pipeline components and integration
"""

import os
import sys
import json
import requests
from typing import Dict, Any

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_test(name: str):
    """Print test header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(message: str):
    """Print success message"""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{RED}✗ {message}{RESET}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{YELLOW}⚠ {message}{RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{BLUE}ℹ {message}{RESET}")


class Phase1Tester:
    """Phase 1 Test Suite"""

    def __init__(self):
        self.api_url = os.getenv("ROSERSG_API_URL", "http://localhost:5000")
        self.api_key = os.getenv("ROSERSG_API_KEY", "default-dev-key")
        self.dspace_url = os.getenv("DSPACE_ENDPOINT", "https://repo.dare.co.zw")
        self.ollama_url = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")

        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

        self.tests_passed = 0
        self.tests_failed = 0

    def run_all_tests(self):
        """Run all Phase 1 tests"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}DARE Research Assistant - Phase 1 Test Suite{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")

        print(f"\nConfiguration:")
        print(f"  API URL: {self.api_url}")
        print(f"  DSpace: {self.dspace_url}")
        print(f"  Ollama: {self.ollama_url}")

        # Run tests
        self.test_api_health()
        self.test_dspace_connection()
        self.test_ollama_connection()
        self.test_chat_endpoint()
        self.test_great_zimbabwe()
        self.test_source_verification()
        self.test_intelligent_search()
        self.test_recommendations()

        # Summary
        self.print_summary()

    def test_api_health(self):
        """Test 1: API Health Check"""
        print_test("API Health Check")

        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            data = response.json()

            if response.status_code == 200 and data.get("status") == "healthy":
                print_success("API is healthy")
                self.tests_passed += 1
            else:
                print_error("API health check failed")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Could not reach API: {e}")
            self.tests_failed += 1

    def test_dspace_connection(self):
        """Test 2: DSpace Connection"""
        print_test("DSpace Connection")

        try:
            response = requests.get(
                f"{self.api_url}/api/dspace/health",
                headers=self.headers,
                timeout=10,
            )
            data = response.json()

            if response.status_code == 200:
                dspace_status = data.get("dspace", {}).get("status")
                if dspace_status == "online":
                    print_success("DSpace is online and accessible")
                    self.tests_passed += 1
                else:
                    print_error(f"DSpace status: {dspace_status}")
                    self.tests_failed += 1
            else:
                print_error(f"DSpace health check failed: {response.status_code}")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Could not check DSpace: {e}")
            self.tests_failed += 1

    def test_ollama_connection(self):
        """Test 3: Ollama Connection"""
        print_test("Ollama Connection")

        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    print_success(f"Ollama is online with {len(models)} model(s)")
                    for model in models:
                        print_info(f"  - {model.get('name')}")
                    self.tests_passed += 1
                else:
                    print_error("No models loaded in Ollama")
                    self.tests_failed += 1
            else:
                print_error(f"Ollama not responding: {response.status_code}")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Could not reach Ollama: {e}")
            self.tests_failed += 1

    def test_chat_endpoint(self):
        """Test 4: Chat Endpoint with RAG"""
        print_test("Chat Endpoint with RAG")

        try:
            payload = {"message": "What is DARE?"}

            response = requests.post(
                f"{self.api_url}/api/chat",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            data = response.json()

            if response.status_code == 200:
                if "response" in data and "sources" in data:
                    print_success("Chat endpoint working")
                    print_info(f"Response: {data['response'][:100]}...")
                    print_info(f"Sources found: {len(data.get('sources', []))}")
                    self.tests_passed += 1
                else:
                    print_error("Invalid response format")
                    print_info(f"Response: {json.dumps(data, indent=2)}")
                    self.tests_failed += 1
            else:
                print_error(f"Chat endpoint failed: {response.status_code}")
                print_info(f"Response: {data}")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Chat endpoint error: {e}")
            self.tests_failed += 1

    def test_great_zimbabwe(self):
        """Test 5: Great Zimbabwe Test Case"""
        print_test("Great Zimbabwe Test Case")

        try:
            payload = {
                "message": "What evidence exists about Great Zimbabwe in the repository?"
            }

            response = requests.post(
                f"{self.api_url}/api/chat",
                json=payload,
                headers=self.headers,
                timeout=60,
            )
            data = response.json()

            if response.status_code == 200:
                answer = data.get("response", "")
                sources = data.get("sources", [])

                if answer and len(answer) > 50:
                    print_success("Generated response about Great Zimbabwe")
                    print_info(f"Response length: {len(answer)} chars")
                else:
                    print_warning("Response seems short or missing")

                if sources:
                    print_success(f"Found {len(sources)} source(s)")
                    for i, source in enumerate(sources[:3], 1):
                        print_info(
                            f"  {i}. {source.get('title')} ({source.get('date')})"
                        )
                    self.tests_passed += 1
                else:
                    print_warning("No sources returned")
                    self.tests_failed += 1
            else:
                print_error(f"Great Zimbabwe test failed: {response.status_code}")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Great Zimbabwe test error: {e}")
            self.tests_failed += 1

    def test_source_verification(self):
        """Test 6: Source Verification"""
        print_test("Source Verification")

        try:
            # First get some sources
            payload = {"message": "Great Zimbabwe"}
            response = requests.post(
                f"{self.api_url}/api/chat",
                json=payload,
                headers=self.headers,
                timeout=60,
            )
            data = response.json()
            sources = data.get("sources", [])

            if not sources:
                print_warning("No sources to verify")
                self.tests_failed += 1
                return

            # Verify each source
            verified = 0
            for source in sources[:3]:  # Check first 3
                uuid = source.get("uuid")
                if not uuid:
                    continue

                try:
                    verify_url = f"{self.dspace_url}/server/api/core/items/{uuid}"
                    verify_response = requests.get(verify_url, timeout=10)

                    if verify_response.status_code == 200:
                        item = verify_response.json()
                        title = item.get("name")
                        print_success(
                            f"Verified source: {title[:50]}... (UUID: {uuid[:8]}...)"
                        )
                        verified += 1
                    else:
                        print_error(f"Could not verify UUID {uuid}: {verify_response.status_code}")
                except Exception as e:
                    print_warning(f"Could not verify UUID {uuid}: {e}")

            if verified > 0:
                print_success(f"Verified {verified}/{len(sources[:3])} sources")
                self.tests_passed += 1
            else:
                print_error("Could not verify any sources")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Source verification error: {e}")
            self.tests_failed += 1

    def test_intelligent_search(self):
        """Test 7: Intelligent Search"""
        print_test("Intelligent Search")

        try:
            payload = {"query": "Find research about African history and archaeology"}

            response = requests.post(
                f"{self.api_url}/api/search/intelligent",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            data = response.json()

            if response.status_code == 200:
                if "ai_interpretation" in data and "results" in data:
                    print_success("Intelligent search working")
                    print_info(
                        f"AI interpretation: {data['ai_interpretation'][:100]}..."
                    )
                    print_info(f"Results found: {data.get('results_count', 0)}")
                    self.tests_passed += 1
                else:
                    print_error("Invalid response format")
                    self.tests_failed += 1
            else:
                print_error(f"Intelligent search failed: {response.status_code}")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Intelligent search error: {e}")
            self.tests_failed += 1

    def test_recommendations(self):
        """Test 8: Recommendations"""
        print_test("Recommendations")

        try:
            payload = {"query": "African studies"}

            response = requests.post(
                f"{self.api_url}/api/recommendations",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            data = response.json()

            if response.status_code == 200:
                if "recommendations" in data:
                    recs = data.get("recommendations", [])
                    print_success(f"Got {len(recs)} recommendations")
                    for i, rec in enumerate(recs[:3], 1):
                        print_info(f"  {i}. {rec.get('title')[:50]}...")
                    self.tests_passed += 1
                else:
                    print_error("Invalid response format")
                    self.tests_failed += 1
            else:
                print_error(f"Recommendations failed: {response.status_code}")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Recommendations error: {e}")
            self.tests_failed += 1

    def print_summary(self):
        """Print test summary"""
        total = self.tests_passed + self.tests_failed
        percentage = (
            (self.tests_passed / total * 100) if total > 0 else 0
        )

        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}TEST SUMMARY{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")

        if self.tests_failed == 0:
            print(f"{GREEN}Passed: {self.tests_passed}/{total} ({percentage:.0f}%){RESET}")
            print(f"{GREEN}✓ Phase 1 tests passed!{RESET}")
            return 0
        else:
            print(f"{RED}Passed: {self.tests_passed}/{total} ({percentage:.0f}%){RESET}")
            print(f"{RED}Failed: {self.tests_failed}/{total}{RESET}")
            print(f"{RED}✗ Some tests failed. Check output above.{RESET}")
            return 1


def main():
    """Main test runner"""
    tester = Phase1Tester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
