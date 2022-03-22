from opentera.utils.assets.AssetFile import AssetFile
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class AssetVideoFile(AssetFile):
    video_duration: timedelta = timedelta(0)
