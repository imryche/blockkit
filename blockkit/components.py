from pydantic import BaseModel


class Component(BaseModel):
    def build(self) -> dict:
        return self.dict(by_alias=True, exclude_none=True)
