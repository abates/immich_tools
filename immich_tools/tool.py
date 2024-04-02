#!/usr/bin/python3


from collections import defaultdict
from os import path
import re
import json

import platformdirs

from immich_tools import models

from . import APP_NAME
from .client import Client

class ImmichTool:
    def __init__(self, client: Client):
        self.data_dir = platformdirs.user_data_dir(APP_NAME, ensure_exists=True)
        self.client = client

        self.albums = {}
        self.assets = {}
        self.albums_index = {}

        self._load_cache()
        self._load_albums()

    def _load_cache(self):
        for obj in ["assets", "albums", "albums_index"]:
            setattr(self, obj, {})
            if path.exists(path.join(self.data_dir, f"{obj}.json")):
                with open(path.join(self.data_dir, f"{obj}.json"), encoding="utf8") as file:
                    setattr(self, obj, json.load(file))

    def _save_cache(self, *objects):
        if not objects:
            objects = ["assets"]
        data_dir = platformdirs.user_data_dir("immich_migration", ensure_exists=True)
        for obj in objects:
            with open(path.join(data_dir, f"{obj}.json"), "w", encoding="utf8") as file:
                json.dump(getattr(self, obj), file, indent=4)

    def _load_albums(self):
        if len(self.albums) == 0:
            self.albums = {}
            self.albums_index = {}
            skip = 0
            while albums := self.client.get_albums(skip=skip):
                skip += len(albums)
                for album in albums:
                    print("Reading album", album.album_name)
                    album.pop("assets", None)
                    self.albums[album.id] = album
                    for bucket in self.client.get_buckets(size=models.TimeBucketSize.month, albumId=album.id):
                        assets: list[models.Asset] = self.client.get_bucket_assets(
                            albumId=album.id,
                            size=models.TimeBucketSize.month,
                            timeBucket=bucket,
                        )
                        for asset in assets:
                            self.albums_index.setdefault(asset.id, [])
                            self.albums_index[asset.id].append(album.id)
            self._save_cache("albums", "albums_index")

    def _load_assets(self):
        skip = 0
        if len(self.assets) == 0:
            while assets := self.client.get_assets(skip=skip):
                skip += len(assets)
                for i, asset in enumerate(assets):
                    filename = path.basename(asset.original_path)
                    _, ext = path.splitext(filename)
                    pattern = r"^(.+?)\+\d+(\." + ext.removeprefix(".") + ")$"
                    if match := re.match(pattern, filename):
                        filename = f"{match.group(1)}{match.group(2)}"

                    self.assets.setdefault(filename, {
                        "assets": {},
                    })
                    self.assets[filename]["assets"][asset.id] = asset

                    if i % 100 == 0:
                        self._save_cache()
                self._save_cache()

    def deduplicate(self):
        """Attempt to find and remove duplicate images."""
        albums_for_asset = lambda asset: self.albums_index.get(asset["id"], [])
        album_count = lambda asset: len(albums_for_asset(asset))

        albums: dict[list[str]] = defaultdict(list)
        duplicates = set()
        for group in self.assets.values():
            assets = group["assets"].values()
            if len(assets) > 1:
                assets  = list(reversed(sorted(assets, key=album_count)))
                # make sure all albums are set on assets[0]
                asset_albums = set()
                for asset in assets:
                    asset_albums.update(albums_for_asset(asset))
                    for album in asset_albums:
                        albums[album].append(asset["id"])

                # only mark 1-* as duplicates, keep the first
                duplicates.update([asset["id"] for asset in assets[1:]])

        for album_id, asset_ids in albums.items():
            self.client.add_assets_to_album(album_id, asset_ids)

        self.client.delete_assets(list(duplicates), dry_run=False)
