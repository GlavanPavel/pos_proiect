from pydantic import AnyHttpUrl
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

M = TypeVar('M')

class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description='Number of total items')
    items: List[M] = Field(description='List of items returned in a paginated response')
    next_page: Optional[AnyHttpUrl] = Field(None, description='Next page')
    previous_page: Optional[AnyHttpUrl] = Field(None, description='Previous page')
