import uuid

from fastapi_users import schemas
from pydantic import BaseModel, Field
from typing import Optional
from docx2pdf import convert


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass

class ImageProcessionOptions(BaseModel):
    resize: Optional[str] = Field(None, description="Resize image to given size. Example: 1980x1200")
    convert_to : Optional[str] = Field(None, description="Example: png, webp, jpg, pdf, docx, xlsx, csv")
    grayscale : Optional[bool] = Field(None, description="Convert to greyscale")
    flip : Optional[str] = Field(None, description="gorizontal or vertical")    
    
