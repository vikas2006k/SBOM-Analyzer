from pydantic import BaseModel, Field

class SBOMUploadRequestSchema(BaseModel):
    """Schema for validating application parameters on file upload."""
    application_id: int = Field(..., ge=1, description="Database application key index")

class SBOMUploadResponseSchema(BaseModel):
    """Schema formatting file uploads details outputs."""
    upload_id: int
    file_name: str
    status: str
    uploaded_at: str
