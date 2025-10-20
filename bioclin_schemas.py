"""
Bioclin API Pydantic Schemas
Generated from OpenAPI 3.1.0 specification
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ========== Enums ==========

class RunStatus(str, Enum):
    PENDING = "PENDING"
    LAUNCHING = "LAUNCHING"
    QUEUED = "QUEUED"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


# ========== Base Schemas ==========

class StatusResponse(BaseModel):
    status: int
    message: str


class ValidationError(BaseModel):
    loc: List[str | int]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = None


# ========== User Schemas ==========

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=40)


class UserPublic(BaseModel):
    id: UUID
    active_org_id: UUID
    username: str


class UserPrivate(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    active_org_id: UUID


class UsersPrivate(BaseModel):
    data: List[UserPrivate]
    count: int


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


# ========== Organization Schemas ==========

class OrgCreate(BaseModel):
    name: str
    description: str


class OrgPublic(BaseModel):
    id: UUID
    name: str
    description: str


class OrgPrivate(BaseModel):
    id: UUID
    name: str
    description: str
    is_personal: bool


class OrgsPublic(BaseModel):
    data: List[OrgPublic]
    count: int


class OrgsPrivate(BaseModel):
    data: List[OrgPrivate]
    count: int


class UserContextPrivate(BaseModel):
    user: UserPrivate
    active_org: OrgPrivate
    orgs: OrgsPrivate


# ========== Permission Schemas ==========

class PermissionPrivate(BaseModel):
    id: UUID
    name: str
    description: Optional[str]


class PermissionsPrivate(BaseModel):
    data: List[PermissionPrivate]
    count: int


class RolePrivate(BaseModel):
    id: UUID
    name: str
    description: Optional[str]


class RolesPrivate(BaseModel):
    data: List[RolePrivate]
    count: int


# ========== Parameter Schemas ==========

class ParamCreate(BaseModel):
    name: str
    description: str
    help: str
    type: Optional[str] = "text_box"


class Param(BaseModel):
    id: Optional[UUID] = None
    name: str
    description: str
    help: str
    type: Optional[str] = "text_box"


class ParamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    help: Optional[str] = None
    type: Optional[str] = None


class ParamsPrivate(BaseModel):
    data: List[Param]
    count: int


# ========== Analysis Type Schemas ==========

class AnalysisTypeCreate(BaseModel):
    name: str
    description: str
    image_name: str
    image_hash: str
    param_ids: List[UUID]


class AnalysisType(BaseModel):
    id: Optional[UUID] = None
    name: str
    description: str
    image_name: str
    image_hash: str
    version_status: Optional[str] = "current"
    version_number: Optional[int] = 1
    last_modified: Optional[datetime] = None


class AnalysisTypePrivate(BaseModel):
    id: Optional[UUID] = None
    name: str
    description: str
    image_name: str
    image_hash: str
    version_status: Optional[str] = "current"
    version_number: Optional[int] = 1
    last_modified: Optional[datetime] = None
    params: Optional[List[Param]] = None


class AnalysisTypeUpdate(BaseModel):
    description: Optional[str] = None
    image_name: Optional[str] = None
    image_hash: Optional[str] = None
    param_ids: Optional[List[UUID]] = None


class AnalysisTypesPrivate(BaseModel):
    data: List[AnalysisTypePrivate]
    count: int


# ========== Project Schemas ==========

class ProjectParamCreate(BaseModel):
    param_id: UUID
    pattern: str


class ProjectParamPublic(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    help: Optional[str] = None
    pattern: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    analysis_type_id: UUID
    project_params: Optional[List[ProjectParamCreate]] = None


class ProjectPublic(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    google_bucket: str
    organization_name: str
    analysis_type_name: str
    n_runs: int
    project_params: Optional[List[ProjectParamPublic]] = None


class ProjectsPublic(BaseModel):
    data: List[ProjectPublic]
    count: int


# ========== Run Schemas ==========

class RunCreate(BaseModel):
    name: str
    project_id: UUID


class RunParamPublic(BaseModel):
    name: str
    description: Optional[str] = None
    help: Optional[str] = None
    pattern: str
    value: Optional[str] = None


class Run(BaseModel):
    id: Optional[UUID] = None
    name: str
    status: RunStatus = RunStatus.PENDING
    status_detail: Optional[str] = None
    n_files_received: int = 0
    n_files_expected: int = 0
    job_uid: Optional[str] = None
    result_path: Optional[str] = None
    recipients: List[EmailStr]
    created_at: datetime
    project_id: UUID


class RunPrivate(BaseModel):
    id: UUID
    name: str
    status: RunStatus
    status_detail: Optional[str] = None
    job_uid: Optional[str] = None
    result_path: Optional[str] = None
    recipients: Optional[List[EmailStr]] = None
    created_at: datetime
    project: ProjectPublic
    run_params: Optional[List[RunParamPublic]] = None


class RunsPrivate(BaseModel):
    data: List[RunPrivate]
    count: int


# ========== OAuth Schemas ==========

class BodyLogin(BaseModel):
    model_config = ConfigDict(extra='allow')

    grant_type: Optional[str] = Field(None, pattern="^password$")
    username: str
    password: str
    scope: str = ""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
