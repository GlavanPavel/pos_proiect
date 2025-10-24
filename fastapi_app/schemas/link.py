from typing import Optional

from pydantic import BaseModel

class Link(BaseModel):
    href: str
    method: str = "GET"

class LinkCollection(BaseModel):
    self: Link
    parent: Optional[Link] = None
