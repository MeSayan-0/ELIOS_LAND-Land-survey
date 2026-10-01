from pathlib import Path

from PIL import Image


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
}

GNSS_EXTENSIONS = {
    ".obs",
    ".rnx",
    ".nav",
}

CSV_EXTENSIONS = {
    ".csv",
}

FLIGHT_LOG_EXTENSIONS = {
    ".log",
}


def validate_image(file_path: str) -> tuple[str, str]:
    path = Path(file_path)

    try:
        with Image.open(path) as image:
            image.verify()

        with Image.open(path) as image:
            width, height = image.size
            image_format = image.format

            if width <= 0 or height <= 0:
                return "INVALID", "Image has invalid dimensions."

            return (
                "VALID",
                (
                    f"Image is readable: "
                    f"{width}x{height}, format={image_format}."
                ),
            )

    except Exception as exc:
        return "INVALID", f"Image could not be read: {exc}"


def validate_file(
    file_path: str,
    file_type: str,
) -> tuple[str, str]:
    path = Path(file_path)

    if not path.exists():
        return "INVALID", "Stored file does not exist."

    if not path.is_file():
        return "INVALID", "Stored path is not a regular file."

    if path.stat().st_size == 0:
        return "INVALID", "File is empty."

    extension = path.suffix.lower()

    if file_type == "IMAGE":
        if extension not in IMAGE_EXTENSIONS:
            return "WARNING", "Image extension is not recognized."

        return validate_image(file_path)

    if file_type in {
        "GNSS_OBSERVATION",
        "GNSS_NAVIGATION",
        "GNSS_RINEX",
    }:
        if extension not in GNSS_EXTENSIONS:
            return "WARNING", "GNSS file extension is not recognized."

        return "VALID", "GNSS file passed basic file validation."

    if file_type == "CSV":
        if extension not in CSV_EXTENSIONS:
            return "WARNING", "CSV file extension is not recognized."

        return "VALID", "CSV file passed basic file validation."

    if file_type == "FLIGHT_LOG":
        if extension not in FLIGHT_LOG_EXTENSIONS:
            return "WARNING", "Flight log extension is not recognized."

        return "VALID", "Flight log passed basic file validation."

    return "WARNING", (
        "File exists and is not empty, but no specialized validator "
        f"exists yet for type {file_type}."
    )
