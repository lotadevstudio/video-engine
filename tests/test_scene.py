from src.scene.processor import process_scene


scene = {
    "number": 1,
    "title": "The Beginning",
    "narration": (
        "Long before the modern world existed, "
        "a small community lived in the heart of the forest."
    )
}

project_dir = "output/my-first-documentary"

process_scene(
    project_dir=project_dir,
    scene=scene,
    provider="edge"
)