from pathlib import Path
from time import sleep

from dotenv import load_dotenv

from src.visuals.generator import generate_image


# Project configuration
ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")

OUTPUT_DIR = ROOT_DIR / "output" / "visual-test"

# Reference images must be smaller than 512x512.
REFERENCE_WIDTH = 480
REFERENCE_HEIGHT = 270

# Final composition
FINAL_WIDTH = 1024
FINAL_HEIGHT = 576

OVERWRITE = False


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    character_path = OUTPUT_DIR / "character.png"
    location_path = OUTPUT_DIR / "location.png"
    scene_path = OUTPUT_DIR / "combined_scene.png"

    # ========================================================
    # 1. GENERATE CHARACTER
    # ========================================================

    print("\nPHASE 1: GENERATING CHARACTER")

    character_prompt = """
    A full-body stylized 3D male character for an educational
    documentary.

    Simple recognizable design, clean white clothing,
    expressive face, realistic 3D materials and soft studio
    lighting.

    Standing in a neutral pose, facing the camera.
    Plain light grey background.

    Professional 3D animation quality.
    No text, no watermark.
    """

    generate_image(
        prompt=character_prompt,
        output_path=character_path,
        source="ai",
        provider="cloudflare",
        width=REFERENCE_WIDTH,
        height=REFERENCE_HEIGHT,
        overwrite=OVERWRITE
    )

    # ========================================================
    # 2. GENERATE LOCATION
    # ========================================================

    print("\nPHASE 2: GENERATING LOCATION")

    location_prompt = """
    A cinematic 3D environment of an ancient village
    surrounded by a dense green forest.

    Small wooden houses, natural materials, trees,
    a dirt pathway and warm morning sunlight.

    Wide establishing shot.
    Professional educational documentary visual style.

    No people, no characters, no text, no watermark.
    """

    generate_image(
        prompt=location_prompt,
        output_path=location_path,
        source="ai",
        provider="cloudflare",
        width=REFERENCE_WIDTH,
        height=REFERENCE_HEIGHT,
        overwrite=OVERWRITE
    )

    # ========================================================
    # 3. COMBINE CHARACTER AND LOCATION
    # ========================================================

    print("\nPHASE 3: GENERATING COMBINED SCENE")

    combined_prompt = """
    Create a cinematic 3D documentary scene.

    CHARACTER REFERENCE:
    The FIRST input image is the character reference.
    Preserve the character's identity, appearance,
    clothing, proportions and materials.

    LOCATION REFERENCE:
    The SECOND input image is the environment reference.
    Preserve its architectural identity, environment,
    materials, colour palette and lighting.

    SCENE:
    Place the referenced character naturally inside
    the referenced village environment.

    Show him standing on the dirt pathway,
    looking towards the village.

    Keep the character recognizable and the environment
    visually consistent with both reference images.

    Professional cinematic 3D composition.
    No text, captions or watermark.
    """

    generate_image(
        prompt=combined_prompt,
        output_path=scene_path,
        source="ai",
        provider="cloudflare",
        reference_images=[
            character_path,
            location_path
        ],
        width=FINAL_WIDTH,
        height=FINAL_HEIGHT,
        overwrite=OVERWRITE
    )

    print("\n" + "=" * 50)
    print("VISUAL GENERATION EXPERIMENT COMPLETED")
    print("=" * 50)

    print(f"Character: {character_path}")
    print(f"Location: {location_path}")
    print(f"Combined: {scene_path}")


if __name__ == "__main__":
    main()