import os
from io import BytesIO
from uuid import uuid4

try:
    import cloudinary
    import cloudinary.uploader
    from cloudinary.exceptions import Error as CloudinaryError
    HAS_CLOUDINARY = True
except ImportError:
    HAS_CLOUDINARY = False
    class DummyUploader:
        @staticmethod
        def upload(*args, **kwargs):
            return {}
    class DummyCloudinary:
        uploader = DummyUploader()
        @staticmethod
        def config(**kwargs):
            pass
    cloudinary = DummyCloudinary()
    class CloudinaryError(Exception):
        pass


class CloudinaryNotConfiguredError(RuntimeError):
    pass


class CloudinaryUploadError(RuntimeError):
    pass


def is_cloudinary_configured() -> bool:
    url = os.getenv("CLOUDINARY_URL")
    credentials = (
        os.getenv("CLOUDINARY_CLOUD_NAME"),
        os.getenv("CLOUDINARY_API_KEY"),
        os.getenv("CLOUDINARY_API_SECRET"),
    )
    if url:
        return True
    if any(credentials) and not all(credentials):
        raise CloudinaryNotConfiguredError(
            "Set CLOUDINARY_URL or all three Cloudinary credential variables."
        )
    return bool(all(credentials))


def upload_food_image(image_bytes: bytes, filename: str) -> str:
    if not is_cloudinary_configured():
        raise CloudinaryNotConfiguredError(
            "Cloudinary image storage is not configured."
        )

    config = {"secure": True}
    if not os.getenv("CLOUDINARY_URL"):
        config.update(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        )
    cloudinary.config(**config)

    try:
        result = cloudinary.uploader.upload(
            BytesIO(image_bytes),
            folder=os.getenv("CLOUDINARY_UPLOAD_FOLDER", "safebite/food-scans"),
            public_id=uuid4().hex,
            resource_type="image",
            overwrite=False,
            filename_override=os.path.basename(filename),
        )
    except CloudinaryError as exc:
        raise CloudinaryUploadError("Cloudinary rejected the image upload.") from exc

    image_url = result.get("secure_url")
    if not isinstance(image_url, str) or not image_url.startswith("https://"):
        raise CloudinaryUploadError("Cloudinary did not return a secure image URL.")
    return image_url
