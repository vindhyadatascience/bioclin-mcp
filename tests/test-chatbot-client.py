#!/usr/bin/env python3
"""
Unit and Integration Tests for Bioclin Chatbot Client

Run with:
    python -m pytest test-chatbot-client.py -v
    or
    python test-chatbot-client.py
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'chatbot'))

from bioclin_chatbot_client import BioclinChatbotClient, BioclinSession


class TestBioclinChatbotClient:
    """Test suite for BioclinChatbotClient"""

    def __init__(self):
        self.mcpx_url = os.getenv("MCPX_URL", "http://localhost:9000")
        self.bioclin_email = os.getenv("BIOCLIN_EMAIL", "test@example.com")
        self.bioclin_password = os.getenv("BIOCLIN_PASSWORD", "password")

        # OAuth config (optional)
        self.oauth_config = None
        if all([
            os.getenv("AUTH0_DOMAIN"),
            os.getenv("AUTH0_CLIENT_ID"),
            os.getenv("AUTH0_CLIENT_SECRET")
        ]):
            self.oauth_config = {
                "token_url": f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
                "client_id": os.getenv("AUTH0_CLIENT_ID"),
                "client_secret": os.getenv("AUTH0_CLIENT_SECRET"),
                "audience": "mcpx-bioclin"
            }

        self.results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }

    def log_pass(self, test_name: str):
        print(f"✓ PASS: {test_name}")
        self.results["passed"] += 1

    def log_fail(self, test_name: str, error: str):
        print(f"✗ FAIL: {test_name}")
        print(f"  Error: {error}")
        self.results["failed"] += 1

    def log_skip(self, test_name: str, reason: str):
        print(f"⊘ SKIP: {test_name} ({reason})")
        self.results["skipped"] += 1

    async def test_client_initialization(self):
        """Test 1: Client can be initialized"""
        test_name = "Client Initialization"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config,
                consumer_tag="Test"
            )
            assert client.mcpx_url == self.mcpx_url
            assert client.consumer_tag == "Test"
            self.log_pass(test_name)
        except Exception as e:
            self.log_fail(test_name, str(e))

    async def test_context_manager(self):
        """Test 2: Client works as async context manager"""
        test_name = "Async Context Manager"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config
            )

            async with client:
                assert client.http_client is not None
                if self.oauth_config:
                    assert client.session.access_token is not None

            # After exit, client should be closed
            assert client.http_client.is_closed

            self.log_pass(test_name)
        except Exception as e:
            self.log_fail(test_name, str(e))

    async def test_list_tools(self):
        """Test 3: Can list MCP tools"""
        test_name = "List MCP Tools"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config
            )

            async with client:
                tools = await client.list_tools()

                assert isinstance(tools, list)
                assert len(tools) > 0

                # Check for some Bioclin tools
                tool_names = [t["name"] for t in tools]
                assert "bioclin_login" in tool_names
                assert "bioclin_get_user_me" in tool_names

                self.log_pass(f"{test_name} (found {len(tools)} tools)")

        except Exception as e:
            self.log_fail(test_name, str(e))

    async def test_bioclin_login(self):
        """Test 4: Can login to Bioclin"""
        test_name = "Bioclin Login"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config
            )

            async with client:
                result = await client.login_bioclin(
                    self.bioclin_email,
                    self.bioclin_password
                )

                # Check for successful login (no error field)
                if "error" in result:
                    self.log_fail(test_name, result["error"])
                else:
                    assert client.session.bioclin_logged_in is True
                    self.log_pass(test_name)

        except Exception as e:
            self.log_fail(test_name, str(e))

    async def test_get_user_info(self):
        """Test 5: Can get user info after login"""
        test_name = "Get User Info"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config
            )

            async with client:
                # Login first
                await client.login_bioclin(
                    self.bioclin_email,
                    self.bioclin_password
                )

                # Get user info
                user_info = await client.get_user_info()

                assert "id" in user_info
                assert "username" in user_info
                assert "email" in user_info

                self.log_pass(f"{test_name} (user: {user_info['username']})")

        except Exception as e:
            self.log_fail(test_name, str(e))

    async def test_get_user_context(self):
        """Test 6: Can get user context"""
        test_name = "Get User Context"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config
            )

            async with client:
                await client.login_bioclin(
                    self.bioclin_email,
                    self.bioclin_password
                )

                context = await client.get_user_context()

                assert "user" in context
                assert "active_org" in context
                assert "orgs" in context

                self.log_pass(f"{test_name} (org: {context['active_org']['name']})")

        except Exception as e:
            self.log_fail(test_name, str(e))

    async def test_list_projects(self):
        """Test 7: Can list projects"""
        test_name = "List Projects"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config
            )

            async with client:
                await client.login_bioclin(
                    self.bioclin_email,
                    self.bioclin_password
                )

                projects = await client.list_projects()

                assert "data" in projects
                assert "count" in projects
                assert isinstance(projects["data"], list)

                self.log_pass(f"{test_name} (found {projects['count']} projects)")

        except Exception as e:
            self.log_fail(test_name, str(e))

    async def test_list_analysis_types(self):
        """Test 8: Can list analysis types"""
        test_name = "List Analysis Types"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config
            )

            async with client:
                await client.login_bioclin(
                    self.bioclin_email,
                    self.bioclin_password
                )

                types = await client.list_analysis_types()

                assert "data" in types
                assert "count" in types

                self.log_pass(f"{test_name} (found {types['count']} types)")

        except Exception as e:
            self.log_fail(test_name, str(e))

    async def test_list_organizations(self):
        """Test 9: Can list organizations"""
        test_name = "List Organizations"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config
            )

            async with client:
                await client.login_bioclin(
                    self.bioclin_email,
                    self.bioclin_password
                )

                orgs = await client.list_organizations()

                assert "data" in orgs
                assert "count" in orgs

                self.log_pass(f"{test_name} (found {orgs['count']} orgs)")

        except Exception as e:
            self.log_fail(test_name, str(e))

    async def test_error_handling(self):
        """Test 10: Properly handles errors"""
        test_name = "Error Handling"
        try:
            client = BioclinChatbotClient(
                mcpx_url=self.mcpx_url,
                oauth_config=self.oauth_config
            )

            async with client:
                # Try to call a tool that doesn't exist
                try:
                    await client.call_tool("nonexistent_tool", {})
                    self.log_fail(test_name, "Should have raised an error")
                except Exception as e:
                    # Expected to fail
                    self.log_pass(f"{test_name} (correctly raised error)")

        except Exception as e:
            self.log_fail(test_name, str(e))

    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 50)
        print("Bioclin Chatbot Client Test Suite")
        print("=" * 50)
        print(f"MCPX URL: {self.mcpx_url}")
        print(f"OAuth: {'Enabled' if self.oauth_config else 'Disabled'}")
        print()

        # Run tests
        await self.test_client_initialization()
        await self.test_context_manager()
        await self.test_list_tools()
        await self.test_bioclin_login()
        await self.test_get_user_info()
        await self.test_get_user_context()
        await self.test_list_projects()
        await self.test_list_analysis_types()
        await self.test_list_organizations()
        await self.test_error_handling()

        # Print summary
        print()
        print("=" * 50)
        print("Test Summary")
        print("=" * 50)
        print(f"Passed:  {self.results['passed']}")
        print(f"Failed:  {self.results['failed']}")
        print(f"Skipped: {self.results['skipped']}")
        print()

        if self.results['failed'] == 0:
            print("✓ All tests passed!")
            return 0
        else:
            print("✗ Some tests failed")
            return 1


async def main():
    """Main entry point"""
    tester = TestBioclinChatbotClient()
    exit_code = await tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
