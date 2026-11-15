import base64
import mimetypes
import os
from contextlib import ExitStack
from pathlib import Path

import requests


def generate(
    prompt,
    output_path,
    reference_images=None,
    width=1024,
    height=1024,
    overwrite=False
):
    """Generate an image using Cloudflare Workers AI."""

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Image prompt cannot be empty.")

    output_path = Path(output_path)

    if output_path.is_file() and output_path.stat().st_size > 0 and not overwrite:
        print(f"Image already exists. Skipping: {output_path}")
        return output_path

    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")

    model = os.getenv(
        "CLOUDFLARE_IMAGE_MODEL",
        "@cf/black-forest-labs/flux-2-klein-4b"
    )

    if not account_id or not api_token:
        raise ValueError("Missing Cloudflare credentials in .env")

    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{account_id}/ai/run/{model}"
    )

    headers = {
        "Authorization": f"Bearer {api_token}"
    }

    files = {
        "prompt": (None, prompt),
        "width": (None, str(width)),
        "height": (None, str(height))
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = output_path.with_name(
        output_path.stem + ".tmp" + output_path.suffix
    )

    try:
        with ExitStack() as stack:

            # Attach reference images in the requested order.
            if reference_images:
                for index, image_path in enumerate(reference_images):

                    image_path = Path(image_path)

                    if not image_path.is_file():
                        raise FileNotFoundError(
                            f"Reference image missing: {image_path}"
                        )

                    file_handle = stack.enter_context(
                        image_path.open("rb")
                    )

                    mime_type = (
                        mimetypes.guess_type(image_path.name)[0]
                        or "application/octet-stream"
                    )

                    files[f"input_image_{index}"] = (
                        image_path.name,
                        file_handle,
                        mime_type
                    )

            print(f"Generating image: {output_path.name}")

            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=300
            )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if "application/json" in content_type:
            data = response.json()

            if not data.get("success", True):
                raise RuntimeError(
                    f"Cloudflare generation failed: {data}"
                )

            image_base64 = data["result"]["image"]
            image_bytes = base64.b64decode(image_base64)

        else:
            image_bytes = response.content

        if not image_bytes:
            raise RuntimeError("Cloudflare returned an empty image.")

        with temp_path.open("wb") as output_file:
            output_file.write(image_bytes)

        temp_path.replace(output_path)

        print(f"Image generated successfully: {output_path}")

        return output_path

    except requests.RequestException as error:
        raise RuntimeError(
            f"Cloudflare request failed: {error}"
        ) from error

    finally:
        if temp_path.exists():
            temp_path.unlink()