"""The immich python client."""

import json
from typing import Any, Union, List, Dict

import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from . import models
from .config import Settings

URLParams = dict[str, Any]
RequestData = Union[list[Any], dict[str, Any]]
JsonType = Union[None, int, str, bool, List["JsonType"], Dict[str, "JsonType"]]


class Client:
    """A simple client for interacting with the Immich REST API."""

    def __init__(self, base_url: str, api_key: str):
        """Create a new Immich REST client.

        Args:
            base_url (str): The server base URL, e.g. `https://some.server.com/immich`
            api_key (str): An Immich API key configured from the UI.
        """
        if base_url.endswith("/"):
            base_url.removesuffix("/")

        if base_url.endswith("/api"):
            self.base_url = base_url
        else:
            self.base_url = base_url + "/api"

        self.session = requests.Session()
        self.session.headers.update({
          "Accept": "application/json",
          "Content-Type": "application/json",
          "x-api-key": api_key,
        })

    @classmethod
    def connect(cls):
        settings = Settings.load()
        return Client(str(settings.server.endpoint), settings.server.api_key)

    def _do(self, method: str, url: str, params: URLParams=None, data: RequestData=None) -> JsonType:
        """Perform an HTTP action on the given url endpoint.

        Args:
            method (str): The HTTP method to use ("GET", "PUT", "POST", "DELETE")

            url (str): The URL endpoint (not including the base url).

            params (URLParams, optional): HTTP query params to append to the URL. Must be a
              dictionary of simple types (int, float, str, bool, etc) that can be encoded into the 
              URL.

            data (Union[list[Any], dict[str, Any]], optional): Any data to be passed along. The data
              will be serialized with `json.dumps` prior to HTTP request. Defaults to None.

        Returns:
            JsonType: The deserialized JSON response.
        """
        if not url.startswith("/"):
            url = "/" + url

        if isinstance(data, (dict, list)):
            data = json.dumps(data)

        response = self.session.request(
            method=method,
            url=f"{self.base_url}{url}",
            data=data,
            params=params,
            timeout=60,
            verify=False,
        )
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    def add_assets_to_album(self, album_id: str, asset_ids: list[str]):
        """Add a set of assets to an album.

        Args:
            album_id (str): The ID of the `Album` to update.
            asset_ids (list[str]): A list of assets ids to add to the `Album`.
        """
        return self._do("PUT", f"/album/{album_id}/assets", data={"ids": asset_ids})

    def get_buckets(self, size: models.TimeBucketSize, **params) -> list[models.Bucket]:
        """Get a list of asset buckets based on the query parameters."""
        params["size"] = size.value
        response = self._do("GET", "/asset/time-buckets", params=params)
        return models.BucketList.model_validate(response.json())

    def get_bucket_assets(self, bucket: models.Bucket, size: models.TimeBucketSize, **params) -> list[models.Asset]:
        """Get a list of assets for a given bucket.

        Args:
            bucket (models.Bucket): The bucket to fetch from.
            size (models.TimeBucketSize): The size of the bucket used when getting the list of buckets.

        Returns:
            models.AssetList: List of assets in the bucket.
        """
        params["size"] = size.value
        params["timeBucket"] = bucket.time_bucket
        response = self._do("GET", "/asset/time-bucket", params=params)
        return models.AssetList.model_validate(response.json())

    def delete_assets(self, asset_ids: list[str], dry_run=True):
        """Delete a set of assets.

        Args:
            asset_ids (list[str]): A list of asset IDs to be deleted.
            dry_run (bool, optional): Whether or not to actually delete the assets. If `True`
              then only iterate the list of IDs don't actually delete them. Defaults to True.
        """
        print("Deleting", len(asset_ids), "assets")
        while asset_ids:
            data = {
                "force": False,
                "ids": asset_ids[0:1000],
            }
            if not dry_run:
                self._do("DELETE", "/asset", data=data)
            asset_ids = asset_ids[1000:]

        return

    def get_albums(self, **params) -> list[models.Album]:
        """Get a list of assets based on the given search params.

        Returns:
            models.AlbumList: The list of albums found based on the search criteria.
        """
        return models.AlbumList.model_validate(self._do("GET", "/album", params=params))


    def get_assets(self, **params) -> list[models.Asset]:
        """Get a list of assets based on the given search params.

        Returns:
            models.AssetList: The list of assets found based on the search criteria.
        """
        return models.AssetList.model_validate(self._do("GET", "/asset", params=params))
