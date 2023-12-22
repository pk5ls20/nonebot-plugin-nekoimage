import io
import json
import uuid
import httpx
from enum import Enum
from nonebot import get_driver
from pydantic import BaseModel, Field, constr

config = get_driver().config


class ApiRouteEnum(str, Enum):
    text = f"{config.nekoimageapi}/search/text/"
    image = f"{config.nekoimageapi}/search/image"
    similar = f"{config.nekoimageapi}/search/similar/"
    random = f"{config.nekoimageapi}/search/random"
    advanced = f"{config.nekoimageapi}/search/advanced"


class BasisSearchEnum(str, Enum):
    vision = "vision"
    ocr = "ocr"


class SearchModelEnum(str, Enum):
    average = "average"
    best = "best"


class BasicSearchModel(BaseModel):
    count: int = Field(default=10, ge=1, le=100)
    skip: int = Field(default=0, ge=0)

    def __call__(self, *args, **kwargs):
        return self.payload, self.url

    @property
    def payload(self):
        return self.dict(by_alias=True, exclude_unset=True)

    @property
    def url(self):
        return f"{ApiRouteEnum[self.__class__.__name__.replace('SearchModel', '').lower()].value}"

    class Config:
        use_enum_values = True


class TextSearchModel(BasicSearchModel):
    prompt: constr(min_length=2)
    basis: BasisSearchEnum

    @property
    def payload(self):
        return self.dict(by_alias=True, exclude={"prompt"})

    @property
    def url(self):
        return f"{ApiRouteEnum.text.value}{self.prompt}"


class ImageSearchModel(BasicSearchModel):
    image: str

    async def __call__(self, *args, **kwargs):
        pic_data = await self.pic
        return self.payload, self.url, pic_data

    @property
    def payload(self):
        return self.dict(by_alias=True, exclude={"image"})

    @property
    async def pic(self):
        async with httpx.AsyncClient() as client:
            # Fetch the image from the URL
            response = await client.get(self.image)
            response.raise_for_status()
            image_bytes_io = io.BytesIO(response.content)
            return {
                'image': ('file.jpg', image_bytes_io)
            }


class SimilarSearchModel(BasicSearchModel):
    id: uuid.UUID
    basis: BasisSearchEnum

    @property
    def payload(self):
        return self.dict(by_alias=True, exclude={"id"})

    @property
    def url(self):
        return f"{ApiRouteEnum.text.value}{self.id}"


class RandomSearchModel(BasicSearchModel):
    pass


class AdvancedSearchModel(BasicSearchModel):
    criteria: list[str] = Field([], description="The positive criteria you want to search with", max_items=16)
    negative_criteria: list[str] = Field([], description="The negative criteria you want to search with", max_items=16)
    mode: SearchModelEnum = Field(SearchModelEnum.average,
                                  description="The mode you want to use to combine the criteria.")

    def __call__(self, *args, **kwargs):
        return self.payload, self.url, self.body

    @property
    def payload(self):
        return self.dict(exclude={"criteria", "negative_criteria", "mode"})

    @property
    def url(self):
        return f"{ApiRouteEnum.advanced.value}"

    @property
    def body(self):
        return json.dumps(self.dict(include={"criteria", "negative_criteria", "mode"}))
