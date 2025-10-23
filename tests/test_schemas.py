#!/usr/bin/env python3
"""
Unit tests for Bioclin schemas
Tests validation and serialization of all Pydantic models
"""

import pytest
from datetime import datetime
from uuid import uuid4, UUID
from pydantic import ValidationError

from bioclin_schemas import *


class TestEnums:
    """Test enum definitions"""

    def test_run_status_enum(self):
        """Test RunStatus enum values"""
        assert RunStatus.PENDING == "PENDING"
        assert RunStatus.LAUNCHING == "LAUNCHING"
        assert RunStatus.QUEUED == "QUEUED"
        assert RunStatus.SCHEDULED == "SCHEDULED"
        assert RunStatus.RUNNING == "RUNNING"
        assert RunStatus.SUCCEEDED == "SUCCEEDED"
        assert RunStatus.FAILED == "FAILED"


class TestUserSchemas:
    """Test user-related schemas"""

    def test_user_create_valid(self):
        """Test valid UserCreate schema"""
        user = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="SecurePass123"
        )
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@example.com"
        assert user.password == "SecurePass123"

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email"""
        with pytest.raises(ValidationError):
            UserCreate(
                first_name="John",
                last_name="Doe",
                email="invalid-email",
                password="SecurePass123"
            )

    def test_user_create_short_password(self):
        """Test UserCreate with password too short"""
        with pytest.raises(ValidationError):
            UserCreate(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                password="short"
            )

    def test_user_public(self):
        """Test UserPublic schema"""
        user_id = uuid4()
        org_id = uuid4()
        user = UserPublic(
            id=user_id,
            active_org_id=org_id,
            username="johndoe"
        )
        assert user.id == user_id
        assert user.active_org_id == org_id
        assert user.username == "johndoe"

    def test_user_private(self):
        """Test UserPrivate schema"""
        user_id = uuid4()
        org_id = uuid4()
        user = UserPrivate(
            id=user_id,
            first_name="John",
            last_name="Doe",
            username="johndoe",
            email="john@example.com",
            is_admin=False,
            is_active=True,
            active_org_id=org_id
        )
        assert user.id == user_id
        assert user.is_admin is False
        assert user.is_active is True


class TestOrganizationSchemas:
    """Test organization-related schemas"""

    def test_org_create(self):
        """Test OrgCreate schema"""
        org = OrgCreate(
            name="Research Lab",
            description="A research laboratory"
        )
        assert org.name == "Research Lab"
        assert org.description == "A research laboratory"

    def test_org_public(self):
        """Test OrgPublic schema"""
        org_id = uuid4()
        org = OrgPublic(
            id=org_id,
            name="Research Lab",
            description="A research laboratory"
        )
        assert org.id == org_id

    def test_org_private(self):
        """Test OrgPrivate schema"""
        org_id = uuid4()
        org = OrgPrivate(
            id=org_id,
            name="Research Lab",
            description="A research laboratory",
            is_personal=False
        )
        assert org.is_personal is False


class TestParameterSchemas:
    """Test parameter-related schemas"""

    def test_param_create(self):
        """Test ParamCreate schema"""
        param = ParamCreate(
            name="Read Length",
            description="Length of reads",
            help="Enter read length in bp"
        )
        assert param.name == "Read Length"
        assert param.type == "text_box"  # default

    def test_param_create_custom_type(self):
        """Test ParamCreate with custom type"""
        param = ParamCreate(
            name="Genome",
            description="Reference genome",
            help="Select genome",
            type="dropdown"
        )
        assert param.type == "dropdown"

    def test_param(self):
        """Test Param schema"""
        param_id = uuid4()
        param = Param(
            id=param_id,
            name="Read Length",
            description="Length of reads",
            help="Enter read length in bp",
            type="text_box"
        )
        assert param.id == param_id

    def test_param_update(self):
        """Test ParamUpdate schema"""
        param = ParamUpdate(
            name="Updated Name",
            description="Updated description"
        )
        assert param.name == "Updated Name"
        assert param.help is None  # not updated


class TestAnalysisTypeSchemas:
    """Test analysis type schemas"""

    def test_analysis_type_create(self):
        """Test AnalysisTypeCreate schema"""
        param_ids = [uuid4(), uuid4()]
        analysis = AnalysisTypeCreate(
            name="RNA-Seq",
            description="RNA sequencing pipeline",
            image_name="gcr.io/bioclin/rnaseq",
            image_hash="sha256:abc123",
            param_ids=param_ids
        )
        assert analysis.name == "RNA-Seq"
        assert len(analysis.param_ids) == 2

    def test_analysis_type(self):
        """Test AnalysisType schema"""
        analysis_id = uuid4()
        analysis = AnalysisType(
            id=analysis_id,
            name="RNA-Seq",
            description="RNA sequencing pipeline",
            image_name="gcr.io/bioclin/rnaseq",
            image_hash="sha256:abc123"
        )
        assert analysis.id == analysis_id
        assert analysis.version_status == "current"  # default
        assert analysis.version_number == 1  # default

    def test_analysis_type_update(self):
        """Test AnalysisTypeUpdate schema"""
        update = AnalysisTypeUpdate(
            description="Updated description",
            image_hash="sha256:def456"
        )
        assert update.description == "Updated description"
        assert update.image_name is None  # not updated


class TestProjectSchemas:
    """Test project-related schemas"""

    def test_project_param_create(self):
        """Test ProjectParamCreate schema"""
        param_id = uuid4()
        param = ProjectParamCreate(
            param_id=param_id,
            pattern="*.fastq"
        )
        assert param.param_id == param_id
        assert param.pattern == "*.fastq"

    def test_project_create(self):
        """Test ProjectCreate schema"""
        analysis_type_id = uuid4()
        param_id = uuid4()
        project = ProjectCreate(
            name="Test Project",
            description="A test project",
            analysis_type_id=analysis_type_id,
            project_params=[
                ProjectParamCreate(param_id=param_id, pattern="*.fastq")
            ]
        )
        assert project.name == "Test Project"
        assert project.analysis_type_id == analysis_type_id
        assert len(project.project_params) == 1

    def test_project_create_minimal(self):
        """Test ProjectCreate with minimal fields"""
        analysis_type_id = uuid4()
        project = ProjectCreate(
            name="Minimal Project",
            analysis_type_id=analysis_type_id
        )
        assert project.description is None
        assert project.project_params is None

    def test_project_public(self):
        """Test ProjectPublic schema"""
        project_id = uuid4()
        project = ProjectPublic(
            id=project_id,
            name="Test Project",
            google_bucket="bioclin-bucket",
            organization_name="Research Lab",
            analysis_type_name="RNA-Seq",
            n_runs=5
        )
        assert project.id == project_id
        assert project.n_runs == 5


class TestRunSchemas:
    """Test run-related schemas"""

    def test_run_create(self):
        """Test RunCreate schema"""
        project_id = uuid4()
        run = RunCreate(
            name="Test Run",
            project_id=project_id
        )
        assert run.name == "Test Run"
        assert run.project_id == project_id

    def test_run(self):
        """Test Run schema"""
        run_id = uuid4()
        project_id = uuid4()
        now = datetime.now()
        run = Run(
            id=run_id,
            name="Test Run",
            status=RunStatus.PENDING,
            recipients=["user@example.com"],
            created_at=now,
            project_id=project_id
        )
        assert run.id == run_id
        assert run.status == RunStatus.PENDING
        assert run.n_files_received == 0  # default
        assert run.n_files_expected == 0  # default

    def test_run_private(self):
        """Test RunPrivate schema"""
        run_id = uuid4()
        project_id = uuid4()
        now = datetime.now()

        project = ProjectPublic(
            id=project_id,
            name="Test Project",
            google_bucket="bucket",
            organization_name="Org",
            analysis_type_name="Analysis",
            n_runs=1
        )

        run = RunPrivate(
            id=run_id,
            name="Test Run",
            status=RunStatus.RUNNING,
            recipients=["user@example.com"],
            created_at=now,
            project=project
        )
        assert run.status == RunStatus.RUNNING
        assert run.project.id == project_id


class TestOAuthSchemas:
    """Test OAuth-related schemas"""

    def test_body_login(self):
        """Test BodyLogin schema"""
        login = BodyLogin(
            username="user@example.com",
            password="SecurePass123"
        )
        assert login.username == "user@example.com"
        assert login.scope == ""  # default

    def test_body_login_with_grant_type(self):
        """Test BodyLogin with grant_type"""
        login = BodyLogin(
            grant_type="password",
            username="user@example.com",
            password="SecurePass123"
        )
        assert login.grant_type == "password"


class TestStatusSchemas:
    """Test status and error schemas"""

    def test_status_response(self):
        """Test StatusResponse schema"""
        response = StatusResponse(
            status=200,
            message="Success"
        )
        assert response.status == 200
        assert response.message == "Success"

    def test_validation_error(self):
        """Test ValidationError schema"""
        error = ValidationError(
            loc=["body", "email"],
            msg="Invalid email format",
            type="value_error"
        )
        assert error.loc == ["body", "email"]
        assert error.msg == "Invalid email format"


class TestCollectionSchemas:
    """Test collection/list schemas"""

    def test_users_private(self):
        """Test UsersPrivate schema"""
        user_id = uuid4()
        org_id = uuid4()
        users = UsersPrivate(
            data=[
                UserPrivate(
                    id=user_id,
                    first_name="John",
                    last_name="Doe",
                    username="johndoe",
                    email="john@example.com",
                    is_admin=False,
                    is_active=True,
                    active_org_id=org_id
                )
            ],
            count=1
        )
        assert len(users.data) == 1
        assert users.count == 1

    def test_projects_public(self):
        """Test ProjectsPublic schema"""
        project_id = uuid4()
        projects = ProjectsPublic(
            data=[
                ProjectPublic(
                    id=project_id,
                    name="Project 1",
                    google_bucket="bucket",
                    organization_name="Org",
                    analysis_type_name="Analysis",
                    n_runs=0
                )
            ],
            count=1
        )
        assert len(projects.data) == 1
        assert projects.count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
