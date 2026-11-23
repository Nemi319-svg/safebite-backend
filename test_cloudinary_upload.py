import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cloudinary_service
from cloudinary_service import (
    CloudinaryNotConfiguredError,
    is_cloudinary_configured,
    upload_food_image,
)


def test_cloudinary_configuration_requires_complete_credentials(monkeypatch):
    for name in (
        "CLOUDINARY_URL",
        "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY",
        "CLOUDINARY_API_SECRET",
    ):
        monkeypatch.delenv(name, raising=False)
    assert not is_cloudinary_configured()

    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "example-cloud")
    with pytest.raises(CloudinaryNotConfiguredError):
        is_cloudinary_configured()


def test_upload_returns_secure_hosted_url(monkeypatch):
    monkeypatch.setenv("CLOUDINARY_URL", "cloudinary://key:secret@example-cloud")
    upload_options = {}

    def fake_upload(image_file, **options):
        assert image_file.read() == b"image bytes"
        upload_options.update(options)
        return {
            "secure_url": "https://res.cloudinary.com/example/image/upload/food.jpg"
        }

    monkeypatch.setattr(cloudinary_service.cloudinary.uploader, "upload", fake_upload)

    image_url = upload_food_image(b"image bytes", "food.jpg")

    assert image_url == "https://res.cloudinary.com/example/image/upload/food.jpg"
    assert upload_options["folder"] == "safebite/food-scans"
    assert upload_options["resource_type"] == "image"
