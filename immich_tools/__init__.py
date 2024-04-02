"""`immich_tools` is a collection of Python tools for interacting with the Immich REST API."""

from importlib import metadata

app_info = metadata.metadata(__name__)
APP_NAME = app_info['Name']
VERSION = app_info['Version']

__all__ = (
    "APP_NAME",
    "VERSION",
)
