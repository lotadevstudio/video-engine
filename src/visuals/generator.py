from pathlib import Path

from .providers.ai import cloudflare


def generate_image(
    prompt,
    output_path,
    source="ai",
    provider="cloudflare",
    reference_images=None,
    width=1024,
    height=1024,
    overwrite=False
):
    """Generate or retrieve an image using the selected provider."""

    output_path = Path(output_path)

    if source == "ai":

        if provider == "cloudflare":
            return cloudflare.generate(
                prompt=prompt,
                output_path=output_path,
                reference_images=reference_images,
                width=width,
                height=height,
                overwrite=overwrite
            )

        raise ValueError(
            f"Unsupported AI image provider: {provider}"
        )

    elif source == "stock":

        raise NotImplementedError(
            "Stock image providers have not been implemented yet."
        )

    else:
        raise ValueError(
            f"Unsupported image source: {source}"
        )