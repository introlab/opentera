from opentera.utils.assets.BaseAsset import BaseAsset
from dataclasses import dataclass


@dataclass
class AssetFile(BaseAsset):
    file_size: int = 0
    file_name: str = ''

    @property
    def asset_type(self) -> str:
        # Automatically detect mime type from filename
        if self.file_name:
            import mimetypes
            mime = mimetypes.guess_type(self.file_name)[0]
            if mime:
                return mime
        return 'application/octet-stream'
