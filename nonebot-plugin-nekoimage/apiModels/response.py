from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field


class NekoProtocol(BaseModel):
    message: str


class ImageData(BaseModel):
    id: UUID
    url: str
    thumbnail_url: Optional[str] = None
    ocr_text: Optional[str] = None
    image_vector: Optional[Any] = Field(None, exclude=True)
    text_contain_vector: Optional[Any] = Field(None, exclude=True)
    index_date: datetime
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None

    @property
    def payload(self):
        return {
            "url": self.url,
            "thumbnail_url": self.thumbnail_url,
            "ocr_text": self.ocr_text,
            "index_date": self.index_date.isoformat(),
            "width": self.width,
            "height": self.height,
            "aspect_ratio": self.aspect_ratio
        }

    @classmethod
    def from_payload(cls, id: str, payload: dict, vector: Optional[Any] = None):
        return cls(id=UUID(id),
                   url=payload['url'],
                   thumbnail_url=payload['thumbnail_url'],
                   index_date=datetime.fromisoformat(payload['index_date']),
                   ocr_text=payload['ocr_text'] if 'ocr_text' in payload else None,
                   width=payload['width'] if 'width' in payload else None,
                   height=payload['height'] if 'height' in payload else None,
                   aspect_ratio=payload['aspect_ratio'] if 'aspect_ratio' in payload else None,
                   image_vector=vector)


class SearchResult(BaseModel):
    img: ImageData
    score: float


class SearchApiResponse(NekoProtocol):
    query_id: UUID
    result: list[SearchResult]
