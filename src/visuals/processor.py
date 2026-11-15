from pathlib import Path

from .generator import generate_image


def process_references(
    project_dir,
    references,
    source="ai",
    provider="cloudflare",
    width=480,
    height=270,
    overwrite=False
):
    """Generate reusable project-wide visual references."""

    project_dir = Path(project_dir)

    reference_paths = {}

    total = len(references)

    print("\n" + "=" * 55)
    print("PHASE 1: GENERATING PROJECT REFERENCES")
    print("=" * 55)

    for index, reference in enumerate(references, start=1):

        reference_id = reference.get("id")
        prompt = reference.get("prompt")
        output = reference.get("output")

        if not isinstance(reference_id, str) or not reference_id.strip():
            raise ValueError("Reference ID cannot be empty.")

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(
                f"Reference prompt cannot be empty: {reference_id}"
            )

        if not isinstance(output, str) or not output.strip():
            raise ValueError(
                f"Reference output cannot be empty: {reference_id}"
            )

        if reference_id in reference_paths:
            raise ValueError(
                f"Duplicate reference ID: {reference_id}"
            )

        output_path = project_dir / output

        print(
            f"\nReference {index}/{total}: "
            f"{reference_id}"
        )

        generate_image(
            prompt=prompt,
            output_path=output_path,
            source=source,
            provider=provider,
            width=width,
            height=height,
            overwrite=overwrite
        )

        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise RuntimeError(
                f"Reference generation failed: {reference_id}"
            )

        reference_paths[reference_id] = output_path

    print("\nAll project references processed successfully!")

    return reference_paths