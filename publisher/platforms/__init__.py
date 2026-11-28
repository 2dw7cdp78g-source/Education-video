from .base import Platform, PublishError, NotConnected
from .meta import Facebook, Instagram, ACCOUNT_KEY as META_KEY
from .tiktok import TikTok
from .youtube import YouTube

PLATFORMS = {p.name: p for p in (YouTube(), Facebook(), Instagram(), TikTok())}


def account_key(platform):
    return getattr(PLATFORMS[platform], "account_key", platform)


__all__ = ["PLATFORMS", "Platform", "PublishError", "NotConnected", "META_KEY", "account_key"]
