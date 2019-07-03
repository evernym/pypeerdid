from datetime import datetime
import json
from uuid import uuid4


class Delta:
    def __init__(self, change:str, by, when=None, id=None):
        self.change = change
        self.by = by
        if when is None:
            when = datetime.utcnow().isoformat()
        self.when = when
        if id is None:
            id = str(uuid4())
        self.id = id

    @classmethod
    def from_dict(cls, dict):
        return Delta(dict.get("change"), dict.get("by"), dict.get("when"), dict.get("id"))

    @classmethod
    def from_json(cls, json_text):
        return Delta.from_dict(json.loads(json_text))

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.to_json()