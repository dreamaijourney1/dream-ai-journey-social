import base64
import os
from pathlib import Path

import openai


openai_client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "")
)


def generate_and_save_images(
    week_of: str,
    days: list[dict],
) -> list[dict]:
    result = []

    image_dir = Path(f"images/{week_of}")
    image_dir.mkdir(parents=True, exist_ok=True)

    for i, day in enumerate(days):
        print(f"Generating image {i + 1} of {len(days)}...")

        response = openai_client.images.generate(
            model="gpt-image-2",
            prompt=day["image_prompt"],
            size="1024x1024",
            quality="medium",
            n=1,
        )

        image_base64 = response.data[0].b64_json

        if not image_base64:
            raise ValueError(
                f"OpenAI did not return image data for day {i + 1}."
            )

        image_bytes = base64.b64decode(image_base64)

        image_path = image_dir / f"day-{i + 1}.png"
        image_path.write_bytes(image_bytes)

        print(f"Saved image to {image_path}")

        result.append(
            {
                **day,
                "image_path": image_path.as_posix(),
            }
        )

    return result
