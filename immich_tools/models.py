from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, RootModel


class Album(BaseModel):
    album_name: str = Field(alias='albumName')
    album_thumbnail_asset_id: str = Field(alias='albumThumbnailAssetId')
    asset_count: int = Field(alias='assetCount')
    assets: List["Asset"]
    created_at: datetime = Field(alias='createdAt')
    description: str
    end_date: Optional[datetime] = Field(None, alias='endDate')
    has_shared_link: bool = Field(alias='hasSharedLink')
    id: str
    is_activity_enabled: bool = Field(alias='isActivityEnabled')
    last_modified_asset_timestamp: Optional[datetime] = Field(
        None, alias='lastModifiedAssetTimestamp'
    )
    owner: "User"
    owner_id: str = Field(alias='ownerId')
    shared: bool
    shared_users: List["User"] = Field(alias='sharedUsers')
    start_date: Optional[datetime] = Field(None, alias='startDate')
    updated_at: datetime = Field(alias='updatedAt')

AlbumList = RootModel[List[Album]]

class Asset(BaseModel):
    """Single asset response from the `/asset` endpoints."""

    checksum: str = Field(description='base64 encoded sha1 hash')
    device_asset_id: str = Field(alias='deviceAssetId')
    device_id: str = Field(alias='deviceId')
    duration: str
    exif_info: Optional["ExifData"] = Field(None, alias='exifInfo')
    file_created_at: datetime = Field(alias='fileCreatedAt')
    file_modified_at: datetime = Field(alias='fileModifiedAt')
    has_metadata: bool = Field(alias='hasMetadata')
    id: str
    is_archived: bool = Field(alias='isArchived')
    is_external: bool = Field(alias='isExternal')
    is_favorite: bool = Field(alias='isFavorite')
    is_offline: bool = Field(alias='isOffline')
    is_read_only: bool = Field(alias='isReadOnly')
    is_trashed: bool = Field(alias='isTrashed')
    library_id: str = Field(alias='libraryId')
    live_photo_video_id: Optional[str] = Field(None, alias='livePhotoVideoId')
    local_date_time: datetime = Field(alias='localDateTime')
    original_file_name: str = Field(alias='originalFileName')
    original_path: str = Field(alias='originalPath')
    owner: Optional["User"] = None
    owner_id: str = Field(alias='ownerId')
    people: Optional[List["Person"]] = None
    resized: bool
    smart_info: Optional["SmartInfo"] = Field(None, alias='smartInfo')
    stack: Optional[List["Asset"]] = None
    stack_count: int = Field(alias='stackCount')
    stack_parent_id: Optional[str] = Field(None, alias='stackParentId')
    tags: Optional[List["Tag"]] = None
    thumbhash: str
    type: "AssetTypeEnum"
    updated_at: datetime = Field(alias='updatedAt')

AssetList = RootModel[List["Asset"]]

class AssetTypeEnum(Enum):
    image = 'IMAGE'
    video = 'VIDEO'
    audio = 'AUDIO'
    other = 'OTHER'

class AssetFace(BaseModel):
    bounding_box_x1: int = Field(alias='boundingBoxX1')
    bounding_box_x2: int = Field(alias='boundingBoxX2')
    bounding_box_y1: int = Field(alias='boundingBoxY1')
    bounding_box_y2: int = Field(alias='boundingBoxY2')
    id: UUID
    image_height: int = Field(alias='imageHeight')
    image_width: int = Field(alias='imageWidth')

class Bucket(BaseModel):
    """Single bucket respone from the `/asset/time-buckets` endpoint."""

    count: int
    time_bucket: str = Field(alias="timeBucket")

BucketList= RootModel[List["Bucket"]]


class ExifData(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    date_time_original: Optional[datetime] = Field(None, alias='dateTimeOriginal')
    description: Optional[str] = None
    exif_image_height: Optional[float] = Field(None, alias='exifImageHeight')
    exif_image_width: Optional[float] = Field(None, alias='exifImageWidth')
    exposure_time: Optional[str] = Field(None, alias='exposureTime')
    f_number: Optional[float] = Field(None, alias='fNumber')
    file_size_in_byte: Optional[int] = Field(None, alias='fileSizeInByte')
    focal_length: Optional[float] = Field(None, alias='focalLength')
    iso: Optional[float] = None
    latitude: Optional[float] = None
    lens_model: Optional[str] = Field(None, alias='lensModel')
    longitude: Optional[float] = None
    make: Optional[str] = None
    model: Optional[str] = None
    modify_date: Optional[datetime] = Field(None, alias='modifyDate')
    orientation: Optional[str] = None
    projection_type: Optional[str] = Field(None, alias='projectionType')
    state: Optional[str] = None
    time_zone: Optional[str] = Field(None, alias='timeZone')

class Person(BaseModel):
    birthDate: date
    faces: List["AssetFace"]
    id: str
    isHidden: bool
    name: str
    thumbnailPath: str

class SmartInfo(BaseModel):
    objects: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class Tag(BaseModel):
    id: str
    name: str
    type: "TagTypeEnum"
    user_id: str = Field(alias='userId')

class TagTypeEnum(Enum):
    object = 'OBJECT'
    face = 'FACE'
    custom = 'CUSTOM'

class TimeBucketSize(Enum):
    day = 'DAY'
    month = 'MONTH'

class User(BaseModel):
    avatarColor: "UserAvatarColor"
    createdAt: datetime
    deletedAt: datetime
    email: str
    externalPath: str
    id: str
    isAdmin: bool
    memoriesEnabled: Optional[bool] = None
    name: str
    oauthId: str
    profileImagePath: str
    quotaSizeInBytes: int
    quotaUsageInBytes: int
    shouldChangePassword: bool
    storageLabel: str
    updatedAt: datetime

class UserAvatarColor(Enum):
    primary = 'primary'
    pink = 'pink'
    red = 'red'
    yellow = 'yellow'
    blue = 'blue'
    green = 'green'
    purple = 'purple'
    orange = 'orange'
    gray = 'gray'
    amber = 'amber'
