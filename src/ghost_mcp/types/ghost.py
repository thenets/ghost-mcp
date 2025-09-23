"""Ghost API type definitions based on Ghost v5.0 API."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl


class ContentFormat(str, Enum):
    """Content formats supported by Ghost."""
    LEXICAL = "lexical"
    HTML = "html"
    MOBILEDOC = "mobiledoc"


class PostStatus(str, Enum):
    """Post status options."""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"


class VisibilityType(str, Enum):
    """Content visibility options."""
    PUBLIC = "public"
    MEMBERS = "members"
    PAID = "paid"
    TIERS = "tiers"


class GhostMeta(BaseModel):
    """Ghost API response metadata."""
    pagination: Optional[Dict[str, Any]] = None


class GhostAuthor(BaseModel):
    """Ghost author object."""
    id: str
    name: str
    slug: str
    email: Optional[str] = None
    profile_image: Optional[HttpUrl] = None
    cover_image: Optional[HttpUrl] = None
    bio: Optional[str] = None
    website: Optional[HttpUrl] = None
    location: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    accessibility: Optional[str] = None
    status: str
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    tour: Optional[List[str]] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    roles: Optional[List[Dict[str, Any]]] = None
    url: str


class GhostTag(BaseModel):
    """Ghost tag object."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    feature_image: Optional[HttpUrl] = None
    visibility: VisibilityType = VisibilityType.PUBLIC
    og_image: Optional[HttpUrl] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    twitter_image: Optional[HttpUrl] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    codeinjection_head: Optional[str] = None
    codeinjection_foot: Optional[str] = None
    canonical_url: Optional[HttpUrl] = None
    accent_color: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    url: str


class GhostPost(BaseModel):
    """Ghost post object."""
    id: str
    uuid: str
    title: str
    slug: str
    mobiledoc: Optional[str] = None
    lexical: Optional[str] = None
    html: Optional[str] = None
    comment_id: Optional[str] = None
    plaintext: Optional[str] = None
    feature_image: Optional[HttpUrl] = None
    feature_image_alt: Optional[str] = None
    feature_image_caption: Optional[str] = None
    featured: bool = False
    status: PostStatus = PostStatus.DRAFT
    visibility: VisibilityType = VisibilityType.PUBLIC
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    custom_excerpt: Optional[str] = None
    codeinjection_head: Optional[str] = None
    codeinjection_foot: Optional[str] = None
    custom_template: Optional[str] = None
    canonical_url: Optional[HttpUrl] = None
    tags: Optional[List[GhostTag]] = None
    authors: Optional[List[GhostAuthor]] = None
    primary_author: Optional[GhostAuthor] = None
    primary_tag: Optional[GhostTag] = None
    url: str
    excerpt: Optional[str] = None
    reading_time: Optional[int] = None
    access: Optional[bool] = None
    og_image: Optional[HttpUrl] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    twitter_image: Optional[HttpUrl] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    email_segment: Optional[str] = None
    newsletter: Optional[Dict[str, Any]] = None


class GhostPage(BaseModel):
    """Ghost page object."""
    id: str
    uuid: str
    title: str
    slug: str
    mobiledoc: Optional[str] = None
    lexical: Optional[str] = None
    html: Optional[str] = None
    comment_id: Optional[str] = None
    plaintext: Optional[str] = None
    feature_image: Optional[HttpUrl] = None
    feature_image_alt: Optional[str] = None
    feature_image_caption: Optional[str] = None
    featured: bool = False
    status: PostStatus = PostStatus.DRAFT
    visibility: VisibilityType = VisibilityType.PUBLIC
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    custom_excerpt: Optional[str] = None
    codeinjection_head: Optional[str] = None
    codeinjection_foot: Optional[str] = None
    custom_template: Optional[str] = None
    canonical_url: Optional[HttpUrl] = None
    tags: Optional[List[GhostTag]] = None
    authors: Optional[List[GhostAuthor]] = None
    primary_author: Optional[GhostAuthor] = None
    primary_tag: Optional[GhostTag] = None
    url: str
    excerpt: Optional[str] = None
    reading_time: Optional[int] = None
    access: Optional[bool] = None
    og_image: Optional[HttpUrl] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    twitter_image: Optional[HttpUrl] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class GhostMember(BaseModel):
    """Ghost member object."""
    id: str
    uuid: str
    email: str
    name: Optional[str] = None
    note: Optional[str] = None
    subscribed: bool = True
    created_at: datetime
    updated_at: datetime
    labels: Optional[List[Dict[str, Any]]] = None
    avatar_image: Optional[HttpUrl] = None
    comped: bool = False
    email_count: int = 0
    email_opened_count: int = 0
    email_open_rate: Optional[float] = None
    status: str = "free"
    last_seen: Optional[datetime] = None
    newsletters: Optional[List[Dict[str, Any]]] = None
    subscriptions: Optional[List[Dict[str, Any]]] = None
    products: Optional[List[Dict[str, Any]]] = None


class GhostSettings(BaseModel):
    """Ghost settings object."""
    title: str
    description: str
    logo: Optional[HttpUrl] = None
    icon: Optional[HttpUrl] = None
    accent_color: Optional[str] = None
    cover_image: Optional[HttpUrl] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    lang: str = "en"
    timezone: str = "Etc/UTC"
    codeinjection_head: Optional[str] = None
    codeinjection_foot: Optional[str] = None
    navigation: Optional[List[Dict[str, Any]]] = None
    secondary_navigation: Optional[List[Dict[str, Any]]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    og_image: Optional[HttpUrl] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    twitter_image: Optional[HttpUrl] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    url: str


class GhostApiResponse(BaseModel):
    """Ghost API response wrapper."""
    posts: Optional[List[GhostPost]] = None
    pages: Optional[List[GhostPage]] = None
    tags: Optional[List[GhostTag]] = None
    authors: Optional[List[GhostAuthor]] = None
    members: Optional[List[GhostMember]] = None
    settings: Optional[GhostSettings] = None
    meta: Optional[GhostMeta] = None


class GhostError(BaseModel):
    """Ghost API error object."""
    id: str
    message: str
    context: Optional[str] = None
    type: str
    details: Optional[str] = None
    property: Optional[str] = None
    help: Optional[str] = None
    code: Optional[str] = None
    ghostErrorCode: Optional[str] = None


class GhostErrorResponse(BaseModel):
    """Ghost API error response."""
    errors: List[GhostError]