from __future__ import annotations

from .links import platform_of

_PLATFORM_NAMES = {
    "tiktok": "TikTok",
    "youtube": "YouTube",
    "instagram": "Instagram",
    "pinterest": "Pinterest",
}

_REASONS = (
    (
        ("isn't available to everyone", "certain audiences", "age-restricted", "confirm your age"),
        "This post is age- or audience-restricted on {platform}, so it's only visible when logged in.",
    ),
    (
        ("follow this account", "private video", "this account is private"),
        "This post is private on {platform}.",
    ),
    (
        ("login required", "log in", "logged-in", "--cookies"),
        "{platform} only shows this post to logged-in users.",
    ),
    (
        ("rate-limit", "rate limit", "too many requests", "please wait a few minutes"),
        "{platform} is rate-limiting the bot right now. Try again in a few minutes.",
    ),
    (
        ("ip address is blocked", "blocked from accessing"),
        "{platform} blocked access from the bot's server.",
    ),
    (
        ("not available in your country", "geo restrict", "geo-restrict"),
        "This post isn't available in the bot's region.",
    ),
    (
        ("unsupported url",),
        "This type of {platform} link isn't supported.",
    ),
    (
        ("no video formats", "no media", "no downloadable media", "there is no video"),
        "This post has no media the bot can download.",
    ),
    (
        ("private or deleted", "unavailable", "removed", "does not exist", "cannot be found", "404 not found", "error 404"),
        "This post was deleted or is no longer available.",
    ),
    (
        ("timed out", "timeout"),
        "{platform} didn't respond in time. Try again later.",
    ),
)


def explain(error: str, url: str) -> str | None:
    text = error.lower()
    platform = _PLATFORM_NAMES.get(platform_of(url) or "", "The platform")
    for markers, message in _REASONS:
        if any(marker in text for marker in markers):
            return message.format(platform=platform)
    return None
