from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from flexta.utils.validation import does_folder_exist, is_empty_name, is_invalid_path


DEFAULT_TEMPLATE_CONTENT: Dict[str, str] = {
    "index.html": "<!DOCTYPE html>\n"
    "<html lang=\"en\">\n"
    "  <head>\n"
    "    <meta charset=\"UTF-8\" />\n"
    "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
    "    <title>My Flexta Project</title>\n"
    "    <link rel=\"stylesheet\" href=\"styles.css\" />\n"
    "  </head>\n"
    "  <body>\n"
    "    <main class=\"app\">\n"
    "      <h1>Welcome to Flexta</h1>\n"
    "      <p>Edit this project to get started.</p>\n"
    "      <button id=\"action\">Click me</button>\n"
    "    </main>\n"
    "    <script src=\"script.js\"></script>\n"
    "  </body>\n"
    "</html>\n",
    "styles.css": ":root {\n"
    "  color-scheme: light dark;\n"
    "  font-family: 'Segoe UI', system-ui, sans-serif;\n"
    "}\n\n"
    "body {\n"
    "  margin: 0;\n"
    "  padding: 0;\n"
    "  min-height: 100vh;\n"
    "  display: grid;\n"
    "  place-items: center;\n"
    "  background: #0f172a;\n"
    "  color: #e2e8f0;\n"
    "}\n\n"
    ".app {\n"
    "  text-align: center;\n"
    "  padding: 3rem;\n"
    "  border-radius: 16px;\n"
    "  background: #1e293b;\n"
    "  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.35);\n"
    "}\n\n"
    "button {\n"
    "  margin-top: 1.5rem;\n"
    "  padding: 0.75rem 1.5rem;\n"
    "  border: none;\n"
    "  border-radius: 999px;\n"
    "  background: #38bdf8;\n"
    "  color: #0f172a;\n"
    "  font-weight: 600;\n"
    "  cursor: pointer;\n"
    "}\n",
    "script.js": "const button = document.getElementById('action');\n"
    "button?.addEventListener('click', () => {\n"
    "  button.textContent = 'Thanks for clicking!';\n"
    "});\n",
}


@dataclass(frozen=True)
class ProjectResult:
    path: Path
    files_written: Dict[str, Path]


def _load_template_file(template_name: str) -> str:
    template_dir = Path(__file__).resolve().parents[1] / "resources" / "templates"
    template_path = template_dir / template_name
    if template_path.exists():
        content = template_path.read_text(encoding="utf-8").strip()
        if content:
            return content + "\n"
    return DEFAULT_TEMPLATE_CONTENT[template_name]


def create_project(project_name: str, base_path: str | Path) -> ProjectResult:
    if is_empty_name(project_name):
        raise ValueError("Project name cannot be empty.")
    if is_invalid_path(base_path):
        raise ValueError("Project location is invalid.")

    base_dir = Path(base_path).expanduser()
    project_dir = base_dir / project_name.strip()

    if does_folder_exist(project_dir):
        raise ValueError("Project folder already exists.")

    project_dir.mkdir(parents=True, exist_ok=False)

    files_written: Dict[str, Path] = {}
    for filename in ("index.html", "styles.css", "script.js"):
        contents = _load_template_file(f"default.{filename.split('.', 1)[1]}")
        file_path = project_dir / filename
        file_path.write_text(contents, encoding="utf-8")
        files_written[filename] = file_path

    return ProjectResult(path=project_dir, files_written=files_written)
