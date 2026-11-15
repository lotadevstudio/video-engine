
import json
import re
import shutil
from pathlib import Path

from src.scene.processor import process_scene
from dotenv import load_dotenv
from src.visuals.processor import process_references


# Project paths
ROOT_DIR = Path(__file__).parent
CONFIG_FILE = ROOT_DIR / "project.json"
OUTPUT_DIR = ROOT_DIR / "output"

# Load Environment variables
load_dotenv(ROOT_DIR / ".env")


def load_config():
    """Load the main project configuration."""

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_slug(title):
    """Convert a video title into a folder-friendly name."""

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")


def initialize_project(config):
    """Create the folder structure for a video project."""

    project = config["project"]
    title = project["title"]

    if not title.strip():
        raise ValueError("Project title cannot be empty.")

    folder_name = create_slug(title)

    if not folder_name:
        raise ValueError("Project title must contain usable characters.")

    project_dir = OUTPUT_DIR / folder_name

    directories = [
        "scenes",
        "shared_assets/images",
        "shared_assets/videos",
        "shared_assets/music",
        "renders"
    ]

    project_dir.mkdir(parents=True, exist_ok=True)

    for directory in directories:
        (project_dir / directory).mkdir(
            parents=True,
            exist_ok=True
        )

    project_config = project_dir / "project.json"

    if not project_config.exists():
        shutil.copy2(CONFIG_FILE, project_config)

    print("\nProject initialized successfully!")
    print(f"Title: {title}")
    print(f"Location: {project_dir}")

    return project_dir



def process_project(config, project_dir):
    """Process project references and all scenes."""

    # Visual settings
    visual_settings = config.get("visuals", {})

    visual_source = visual_settings.get("source", "ai")
    visual_provider = visual_settings.get("provider", "cloudflare")

    # Project rendering settings
    project_settings = config["project"]

    width, height = project_settings["resolution"]
    fps = project_settings.get("fps", 30)

    # Phase 1: Generate reusable project references
    reference_paths = process_references(
        project_dir=project_dir,
        references=visual_settings.get("references", []),
        source=visual_source,
        provider=visual_provider,
        width=480,
        height=270
    )

    # Audio settings
    audio_settings = config.get("audio", {})

    audio_provider = audio_settings.get("provider", "edge")
    voice = audio_settings.get("voice")

    # Phase 2: Process scenes
    for scene in config.get("scenes", []):
        process_scene(
            project_dir=project_dir,
            scene=scene,
            provider=audio_provider,
            voice=voice,
            reference_paths=reference_paths,
            visual_source=visual_source,
            visual_provider=visual_provider,
            width=width,
            height=height,
            fps=fps
        )

    print("\nAll scenes processed successfully!")



def main():
    config = load_config()

    project_dir = initialize_project(config)

    process_project(config, project_dir)


if __name__ == "__main__":
    main()
