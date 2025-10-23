#!/usr/bin/env python3
"""
Example usage of the Bioclin MCP Server
This demonstrates how to interact with the server programmatically
"""

import asyncio
import json
from bioclin_mcp_server import BioclinClient


async def example_authentication():
    """Example: Login and token management"""
    print("\n" + "="*60)
    print("Example 1: Authentication")
    print("="*60)

    client = BioclinClient("http://localhost:8000")

    try:
        # Login
        print("\n1. Logging in...")
        result = await client.request(
            "POST",
            "/api/v1/identity/login",
            form_data={
                "username": "user@example.com",
                "password": "password123",
                "grant_type": "password"
            }
        )
        print(f"Login successful: {json.dumps(result, indent=2)}")

        # Validate token
        print("\n2. Validating token...")
        result = await client.request("POST", "/api/v1/identity/token/validate")
        print(f"Token valid: {json.dumps(result, indent=2)}")

        # Get user info
        print("\n3. Getting user info...")
        result = await client.request("GET", "/api/v1/identity/user_me")
        print(f"User info: {json.dumps(result, indent=2, default=str)}")

    finally:
        await client.close()


async def example_organization_workflow():
    """Example: Complete organization workflow"""
    print("\n" + "="*60)
    print("Example 2: Organization Workflow")
    print("="*60)

    client = BioclinClient("http://localhost:8000")

    try:
        # Login first
        print("\n1. Logging in...")
        await client.request(
            "POST",
            "/api/v1/identity/login",
            form_data={
                "username": "admin@example.com",
                "password": "adminpass",
                "grant_type": "password"
            }
        )

        # Create organization
        print("\n2. Creating organization...")
        org = await client.request(
            "POST",
            "/api/v1/identity/create_org",
            data={
                "name": "Genomics Lab",
                "description": "Research laboratory for genomics studies"
            }
        )
        print(f"Created organization: {json.dumps(org, indent=2, default=str)}")
        org_id = org["id"]

        # Get user context
        print("\n3. Getting user context...")
        context = await client.request(
            "GET",
            "/api/v1/identity/user_context",
            params={"orgs_skip": 0, "orgs_limit": 100}
        )
        print(f"User context: {json.dumps(context, indent=2, default=str)}")

        # Update active org
        print(f"\n4. Switching to organization {org_id}...")
        result = await client.request(
            "PATCH",
            "/api/v1/identity/users/update_active_org",
            params={"org_id": org_id}
        )
        print(f"Active org updated: {json.dumps(result, indent=2, default=str)}")

    finally:
        await client.close()


async def example_project_workflow():
    """Example: Create project and run analysis"""
    print("\n" + "="*60)
    print("Example 3: Project and Run Workflow")
    print("="*60)

    client = BioclinClient("http://localhost:8000")

    try:
        # Login
        print("\n1. Logging in...")
        await client.request(
            "POST",
            "/api/v1/identity/login",
            form_data={
                "username": "researcher@example.com",
                "password": "research123",
                "grant_type": "password"
            }
        )

        # List analysis types
        print("\n2. Getting available analysis types...")
        analysis_types = await client.request(
            "GET",
            "/api/v1/project/analysis_types/",
            params={"skip": 0, "limit": 10}
        )
        print(f"Analysis types: {json.dumps(analysis_types, indent=2, default=str)}")

        # For this example, we'll assume we have an analysis type ID
        # In practice, you'd select from the list above
        analysis_type_id = "123e4567-e89b-12d3-a456-426614174000"

        # Create project
        print("\n3. Creating project...")
        project = await client.request(
            "POST",
            "/api/v1/project/create_project",
            data={
                "name": "RNA-Seq Analysis Project",
                "description": "Analysis of RNA sequencing data",
                "analysis_type_id": analysis_type_id,
                "project_params": [
                    {
                        "param_id": "param-uuid-1",
                        "pattern": "sample_*.fastq"
                    }
                ]
            }
        )
        print(f"Created project: {json.dumps(project, indent=2, default=str)}")
        project_id = project["id"]

        # Create run
        print(f"\n4. Creating run for project {project_id}...")
        run = await client.request(
            "POST",
            "/api/v1/project/create_run",
            data={
                "name": "Sample Batch 001",
                "project_id": project_id
            }
        )
        print(f"Created run: {json.dumps(run, indent=2, default=str)}")
        run_id = run["id"]

        # Get runs for project
        print(f"\n5. Getting all runs for project {project_id}...")
        runs = await client.request(
            "GET",
            "/api/v1/project/runs_by_project",
            params={"project_id": project_id, "skip": 0, "limit": 10}
        )
        print(f"Project runs: {json.dumps(runs, indent=2, default=str)}")

    finally:
        await client.close()


async def example_parameter_and_analysis_type():
    """Example: Create parameters and analysis types"""
    print("\n" + "="*60)
    print("Example 4: Parameters and Analysis Types")
    print("="*60)

    client = BioclinClient("http://localhost:8000")

    try:
        # Login
        print("\n1. Logging in...")
        await client.request(
            "POST",
            "/api/v1/identity/login",
            form_data={
                "username": "admin@example.com",
                "password": "adminpass",
                "grant_type": "password"
            }
        )

        # Create parameters
        print("\n2. Creating parameters...")
        param1 = await client.request(
            "POST",
            "/api/v1/project/create_param",
            data={
                "name": "Read Length",
                "description": "Length of sequencing reads",
                "help": "Specify the read length in base pairs (e.g., 150)",
                "type": "text_box"
            }
        )
        print(f"Created parameter 1: {json.dumps(param1, indent=2, default=str)}")

        param2 = await client.request(
            "POST",
            "/api/v1/project/create_param",
            data={
                "name": "Reference Genome",
                "description": "Reference genome for alignment",
                "help": "Select the reference genome (e.g., hg38, mm10)",
                "type": "text_box"
            }
        )
        print(f"Created parameter 2: {json.dumps(param2, indent=2, default=str)}")

        # Get all parameters
        print("\n3. Listing all parameters...")
        params = await client.request(
            "GET",
            "/api/v1/project/params/",
            params={"skip": 0, "limit": 100}
        )
        print(f"All parameters: {json.dumps(params, indent=2, default=str)}")

        # Create analysis type
        print("\n4. Creating analysis type...")
        analysis_type = await client.request(
            "POST",
            "/api/v1/project/create_analysis_type",
            data={
                "name": "RNA-Seq Pipeline v2",
                "description": "RNA sequencing analysis pipeline version 2",
                "image_name": "gcr.io/bioclin/rnaseq",
                "image_hash": "sha256:abc123...",
                "param_ids": [param1["id"], param2["id"]]
            }
        )
        print(f"Created analysis type: {json.dumps(analysis_type, indent=2, default=str)}")

        # List analysis types
        print("\n5. Listing all analysis types...")
        analysis_types = await client.request(
            "GET",
            "/api/v1/project/analysis_types/",
            params={"skip": 0, "limit": 100}
        )
        print(f"All analysis types: {json.dumps(analysis_types, indent=2, default=str)}")

    finally:
        await client.close()


async def example_user_management():
    """Example: User management operations"""
    print("\n" + "="*60)
    print("Example 5: User Management")
    print("="*60)

    client = BioclinClient("http://localhost:8000")

    try:
        # Create new user (public endpoint)
        print("\n1. Creating new user...")
        user = await client.request(
            "POST",
            "/api/v1/identity/create_user",
            data={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "password": "SecurePass123"
            }
        )
        print(f"Created user: {json.dumps(user, indent=2, default=str)}")

        # Login as admin
        print("\n2. Logging in as admin...")
        await client.request(
            "POST",
            "/api/v1/identity/login",
            form_data={
                "username": "admin@example.com",
                "password": "adminpass",
                "grant_type": "password"
            }
        )

        # List all users
        print("\n3. Listing all users...")
        users = await client.request(
            "GET",
            "/api/v1/identity/users/",
            params={"skip": 0, "limit": 100}
        )
        print(f"All users: {json.dumps(users, indent=2, default=str)}")

        # Set user as admin (using the created user's ID)
        user_id = user["id"]
        print(f"\n4. Setting user {user_id} as admin...")
        result = await client.request(
            "PATCH",
            f"/api/v1/identity/set_user_admin/{user_id}",
            params={"is_admin": True}
        )
        print(f"User updated: {json.dumps(result, indent=2, default=str)}")

    finally:
        await client.close()


async def example_google_cloud_storage():
    """Example: Google Cloud Storage operations"""
    print("\n" + "="*60)
    print("Example 6: Google Cloud Storage")
    print("="*60)

    client = BioclinClient("http://localhost:8000")

    try:
        # Login
        print("\n1. Logging in...")
        await client.request(
            "POST",
            "/api/v1/identity/login",
            form_data={
                "username": "researcher@example.com",
                "password": "research123",
                "grant_type": "password"
            }
        )

        # Generate signed URL for viewing
        print("\n2. Generating signed URL for viewing...")
        url = await client.request(
            "POST",
            "/api/v1/google-ops/generate_signed_url",
            params={
                "bucket_name": "bioclin-results",
                "file_name": "run-123/report.html",
                "response_type": "text/html",
                "expiration_minutes": 60,
                "force_download": False
            }
        )
        print(f"Signed URL (view): {url}")

        # Generate signed URL for download
        print("\n3. Generating signed URL for download...")
        download_url = await client.request(
            "POST",
            "/api/v1/google-ops/generate_signed_url",
            params={
                "bucket_name": "bioclin-results",
                "file_name": "run-123/results.xlsx",
                "expiration_minutes": 30,
                "force_download": True
            }
        )
        print(f"Signed URL (download): {download_url}")

        # Get HTML report
        print("\n4. Getting HTML report...")
        report = await client.request(
            "GET",
            "/api/v1/google-ops/get_html_report",
            params={
                "bucket_name": "bioclin-results",
                "file_name": "run-123/report.html"
            }
        )
        print(f"Report retrieved (first 200 chars): {str(report)[:200]}...")

    finally:
        await client.close()


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("BIOCLIN MCP SERVER - USAGE EXAMPLES")
    print("="*60)
    print("\nNote: These examples assume:")
    print("  - Bioclin API is running at http://localhost:8000")
    print("  - Test accounts exist with the specified credentials")
    print("  - Appropriate UUIDs are used for resources")
    print("\nIn practice, you would replace these with actual values.")
    print("\n" + "="*60)

    # Choose which examples to run
    # Uncomment the ones you want to test

    # await example_authentication()
    # await example_organization_workflow()
    # await example_project_workflow()
    # await example_parameter_and_analysis_type()
    # await example_user_management()
    # await example_google_cloud_storage()

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\nTo run specific examples, edit this file and uncomment")
    print("the desired example functions in the main() function.")


if __name__ == "__main__":
    asyncio.run(main())
