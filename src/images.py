import os
from pathlib import Path

import openai
import requests

openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def generate_and_save_images(week_of: str, days: list[dict]) -> list[dict]:
    result = []
    image_dir = Path(f"images/{week_of}")
    image_dir.mkdir(parents=True, exist_ok=True)

    for i, day in enumerate(days):
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=day["image_prompt"],
            size="1024x1024",
            quality="standard",
            n=1,
        )
        temp_url = response.data[0].url
        image_bytes = requests.get(temp_url).content

        image_path = image_dir / f"day-{i + 1}.png"
        image_path.write_bytes(image_bytes)

        result.append({**day, "image_path": image_path.as_posix()})

    return result
