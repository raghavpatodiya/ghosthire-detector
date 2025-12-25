import os

EXCLUDE_DIRS = {
    "venv", "__pycache__", "node_modules", "build", "dist",
    ".idea", ".vscode", ".pytest_cache"
}

VALID_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".html"}

def count_loc(base_path):
    total = 0

    # Check if path exists before walking to avoid FileNotFoundError
    if not os.path.exists(base_path):
        return 0

    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if any(file.endswith(ext) for ext in VALID_EXTENSIONS):
                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        total += sum(1 for _ in f)
                except Exception:
                    pass

    return total