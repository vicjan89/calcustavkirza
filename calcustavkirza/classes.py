import json


from yaml import load, FullLoader
import tomllib
from pydantic import BaseModel
from textengines.interfaces import TextEngine


class Element(BaseModel):
    name: str | None = None
    # te: TextEngine | None = None
    warning: list | None = None

    def add_context(self, **kwargs):
        self.__dict__.update(kwargs)

    def write_warnings(self, te: TextEngine):
        if self.warning:
            for warning in self.warning:
                te.warning(warning)

    def add_warning(self, msg: str):
        if not self.warning:
            self.warning = []
        self.warning.append(msg)