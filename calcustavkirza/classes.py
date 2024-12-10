import json
from typing import Any

from yaml import load, FullLoader
import tomllib
from pydantic import BaseModel
from textengines.interfaces import TextEngine


class Element(BaseModel):
    name: str | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.name is None:
            self.name = input('Введите имя: ')

    def add_context(self, **kwargs):
        self.__dict__.update(kwargs)


class Doc:
    warning: list | None = None

    def ap_generate(self, te: TextEngine):
        te.ul(self.name)

    def write_warnings(self, te: TextEngine):
        if self.warning:
            for warning in self.warning:
                te.warning(warning)

    def add_warning(self, msg: str):
        if not self.warning:
            self.warning = []
        self.warning.append(msg)
