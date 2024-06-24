import json


from yaml import load, FullLoader
import tomllib
from pydantic import BaseModel
from textengines.interfaces import TextEngine


class Element(BaseModel):
    name: str | None = None
    te: TextEngine | None = None

    def add_context(self, **kwargs):
        self.__dict__.update(kwargs)
