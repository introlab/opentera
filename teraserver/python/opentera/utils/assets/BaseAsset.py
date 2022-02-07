from abc import ABC, abstractmethod
import datetime
from dataclasses import dataclass


@dataclass
class BaseAsset(ABC):
    asset_name: str = ''
    asset_datetime: datetime = datetime.datetime.now()
    asset_uuid: str = ''

    @property
    @abstractmethod
    def asset_type(self) -> str:
        return 'unknown'

    def to_json(self) -> dict:
        attributes = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("_")]
        json = {k: v for k, v in zip([attr for attr in attributes], [getattr(self, attr) for attr in attributes])}

        return json

    def from_json(self, json: dict):
        for key in json.keys():
            if key in dir(self) and not callable(getattr(self, key)) and not key.startswith("_") \
                    and key != 'asset_type':
                setattr(self, key, json[key])

