import logging
import os
import random
from pathlib import Path
from typing import TypedDict

from instagrapi import Client
from PIL import Image

ACCOUNT_USERNAME = os.getenv("INSTAGRAM_USERNAME")
ACCOUNT_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

IMAGE_PATH = Path(os.getenv("INSTAGRAM_IMAGE_PATH", "SET ME PLEASE"))


class PNGMetadata(TypedDict):
    prompt: str
    artist: str
    seed: str
    lyrics: str
    track_artist: str
    track_title: str


def get_png_metadata(image_path: Path) -> PNGMetadata:
    image = Image.open(image_path)
    return {
        "prompt": image.info.get("compviz_prompt", ""),
        "artist": image.info.get("compviz_artist", ""),
        "seed": image.info.get("compviz_seed", ""),
        "lyrics": image.info.get("compviz_lyrics", ""),
        "track_artist": image.info.get("compviz_track_artist", ""),
        "track_title": image.info.get("compviz_track_title", ""),
    }


def generate_caption(image_path: Path) -> str:
    metadata = get_png_metadata(image_path)
    return f"""{metadata['lyrics']}
{metadata["track_artist"]} - {metadata["track_title"]}

As if {metadata["artist"]} painted it

prompt: "{metadata["prompt"]}"

#art #generated #generatedart #stablediffusion #song #{metadata["artist"].replace(" ", "").lower()}
#music #{metadata["track_artist"].replace(" ", "").lower()} #lyrics"""


def upload_image(client: Client, image_path: Path, caption: str, dump_folder: Path):
    jpg_image_path = image_path.with_suffix(".jpg")
    if not jpg_image_path.exists():
        image = Image.open(image_path)
        image.save(image_path.with_suffix(".jpg"), "JPEG")

    logging.info(f"Uploading {image_path} with caption {caption}")
    client.photo_upload(jpg_image_path, caption)
    jpg_image_path.rename(dump_folder / jpg_image_path.name)


def main():
    logging.basicConfig(level=logging.INFO)

    if not ACCOUNT_USERNAME or not ACCOUNT_PASSWORD:
        print(
            "Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables"
        )
        return

    if not IMAGE_PATH.exists():
        print("Please set INSTAGRAM_IMAGE_PATH environment variable")
        return

    cl = Client()
    session_dump_file = Path("session.json")
    if session_dump_file.exists():
        cl.load_settings(session_dump_file)

    cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
    cl.dump_settings(session_dump_file)

    already_uploaded_folder = IMAGE_PATH / "already_uploaded"
    already_uploaded_folder.mkdir(exist_ok=True)
    jpg_folder = IMAGE_PATH / "jpg"
    jpg_folder.mkdir(exist_ok=True)

    image_path = random.choice(list(IMAGE_PATH.glob("*.png")))
    upload_image(cl, image_path, generate_caption(image_path), jpg_folder)
    image_path.rename(already_uploaded_folder / image_path.name)


if __name__ == "__main__":
    main()
