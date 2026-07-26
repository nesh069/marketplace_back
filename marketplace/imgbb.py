import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def upload_image(file) -> str:
    """Upload an image to ImgBB and return the display URL."""
    api_key = settings.IMGBB_API_KEY
    if not api_key:
        logger.warning("IMGBB_API_KEY not set — returning empty string")
        return ""

    try:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": api_key},
            files={"image": file},
            timeout=30,
        )
        data = response.json()
        if response.status_code != 200 or not data.get("success"):
            logger.error("ImgBB upload failed: %s", data.get("error", {}).get("message", response.text))
            return ""
        return data["data"]["display_url"]
    except Exception as e:
        logger.exception("ImgBB upload error: %s", e)
        return ""
