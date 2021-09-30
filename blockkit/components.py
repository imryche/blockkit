from pydantic import BaseModel


class NewComponent(BaseModel):
    def build(self) -> dict:
        return self.dict(exclude_none=True)
