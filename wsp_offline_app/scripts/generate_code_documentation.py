from __future__ import annotations

import ast
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
REFERENCE_ROOT = DOCS_ROOT / "code_reference"
SOURCE_SUFFIXES = {
    ".py",
    ".pyw",
    ".js",
    ".css",
    ".ps1",
    ".bat",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
    ".txt",
    ".gitignore",
}
EXCLUDED_DIRECTORIES = {
    ".git",
    ".models",
    ".pytest_cache",
    ".venv",
    ".vscode",
    "__pycache__",
    "data",
    "dist",
    "docs",
    "testbench_reports",
}


PURPOSES = {
    "main.py": "Creates the startup context, prepares runtime folders/database state, and launches the local FastAPI application through Uvicorn.",
    "config.py": "Defines immutable application settings, runtime modes, filesystem locations, model configuration, and required data directories.",
    "wsp_launcher.pyw": "Provides the Windows desktop/tray launch experience, single-instance behavior, browser opening, process logging, and graceful shutdown controls.",
    "app/web_app.py": "Defines the production FastAPI routes, HTML shell, import orchestration, dashboard APIs, diagnostics, backup endpoints, and request/response adapters.",
    "app/static/wsp.js": "Implements all browser-side interaction: dashboard navigation, filtering, saved preferences, semantic-search progress, data editing, profile navigation, import operations, backup restore, and diagnostics.",
    "app/static/wsp.css": "Defines the complete AUB-branded responsive visual system for navigation, dashboards, tables, profiles, forms, diagnostics, printing, and loading states.",
    "database/models.py": "Declares the SQLite/SQLAlchemy data model for current students, retained history, imports, schemas, filters, exports, embeddings, and backups.",
    "database/db.py": "Creates and configures SQLite engines/sessions, enables safety pragmas, initializes tables, and exposes database health helpers.",
    "database/migrations.py": "Applies lightweight backwards-compatible schema migrations when older local databases are opened.",
    "database/queries.py": "Provides reusable database query helpers for current-student and import-history access.",
    "database/schema_manager.py": "Tracks workbook columns, infers data types, and synchronizes the dynamic column registry.",
    "services/analytics_service.py": "Calculates dashboard metrics, chart series, latest-import summaries, and text-frequency analytics from current records.",
    "services/archive_service.py": "Copies source workbooks into the protected archive and creates pending import-batch records before database changes.",
    "services/backup_service.py": "Creates timestamped SQLite backups, verifies integrity, records backup metadata, and applies retention policy.",
    "services/dashboard_intelligence_service.py": "Builds the placement-focused dashboard model, faculty mappings, worklists, comparison signals, data-quality views, and chart-ready summaries.",
    "services/embedding_service.py": "Loads the local Sentence Transformer model, prepares model-specific query/document text, normalizes vectors, and verifies offline cache availability.",
    "services/excel_importer.py": "Reads Excel workbooks, rejects unsafe inputs, detects duplicates, merges current students, retains history, and logs transactional import results.",
    "services/excel_schema.py": "Defines supported workbook formats and canonical header normalization rules.",
    "services/explanation_service.py": "Turns semantic similarities and original student evidence into short administrator-facing match explanations.",
    "services/export_service.py": "Writes filtered student results and filter metadata into timestamped multi-sheet Excel workbooks and logs exports.",
    "services/filter_service.py": "Validates filter requests, composes SQLAlchemy predicates, applies semantic ranking, sorts/paginates results, and stores filter audit records.",
    "services/folder_watcher.py": "Monitors the configured Import Folder and invokes the import callback for stable supported workbook files.",
    "services/logging_service.py": "Configures local rotating application logs and structured operational logging.",
    "services/preferred_work_grouping_service.py": "Groups free-text work preferences into reviewed, flexible, emerging, or needs-review topics while preserving original responses.",
    "services/semantic_document_service.py": "Builds deterministic original-text semantic profiles and hashes from student fields used by local matching.",
    "services/semantic_search_service.py": "Synchronizes the FAISS student index, ranks embedding matches, cites original-text evidence, manages index freshness, and provides fallbacks.",
    "services/semantic_service.py": "Provides lexical semantic fallbacks, optional local Ollama integration, prompt parsing, and model-availability reporting.",
    "services/student_profile_service.py": "Assembles the holistic student profile payload from current data, retained history, support flags, skills, and extra workbook columns.",
    "services/technical_skill_grouping_service.py": "Splits and semantically groups rough technical-skill text into stable, emerging, or unverified topics without rewriting source data.",
    "services/value_normalizer.py": "Normalizes booleans, numbers, dates, text, email, and phone values while recording non-fatal validation warnings.",
    "services/vector_store_service.py": "Persists normalized vectors and metadata, maintains an in-process cache, and performs candidate-restricted cosine-similarity search.",
    "scripts/install.ps1": "Runs verified one-click Windows installation, including package checksums, Python/venv setup, dependencies, model verification, folders, shortcuts, and final health checks.",
    "scripts/uninstall.ps1": "Removes WSP shortcuts and application files safely, with an option to preserve operational data in a timestamped Documents folder.",
    "scripts/build_release.ps1": "Builds the distributable Windows ZIP, internal SHA-256 manifest, external checksum, and clean release folder structure.",
    "scripts/verify_install.py": "Verifies required modules, writable data paths, SQLite initialization, application routes, and offline embedding generation.",
    "scripts/audit_semantic_index.py": "Audits every stored semantic vector against the current source text and reports coverage, hash consistency, and stale records without modifying data.",
    ".github/workflows/windows-release.yml": "Builds and uploads the verified Windows installer package on main/tag pushes and attaches assets to versioned GitHub Releases.",
}


def source_files() -> list[Path]:
    roots = [ROOT, ROOT.parent / ".github"]
    files: list[Path] = []
    for scan_root in roots:
        if not scan_root.exists():
            continue
        for path in scan_root.rglob("*"):
            if not path.is_file() or any(part in EXCLUDED_DIRECTORIES for part in path.parts):
                continue
            suffix = path.suffix.lower()
            if suffix in SOURCE_SUFFIXES or path.name == ".gitignore":
                files.append(path)
    return sorted(set(files), key=lambda item: display_path(item).casefold())


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.relative_to(ROOT.parent).as_posix()


def doc_path(path: Path) -> Path:
    relative = Path(display_path(path))
    return REFERENCE_ROOT / relative.parent / f"{relative.name}.md"


def purpose_for(path: Path) -> str:
    relative = display_path(path)
    if relative in PURPOSES:
        return PURPOSES[relative]
    if relative.startswith("tests/test_"):
        subject = Path(relative).stem.removeprefix("test_").replace("_", " ")
        return f"Provides regression coverage for {subject}, including expected success paths, validation rules, and failure behavior."
    if relative == "tests/conftest.py":
        return "Defines shared pytest fixtures and reusable test data used across the automated verification suite."
    if relative.startswith("scripts/run_") or relative.startswith("scripts/create_test"):
        return "Supports repeatable development testbench execution and produces auditable local test data or reports."
    if relative.startswith("app/components/"):
        return f"Defines reusable UI data structures and rendering helpers for the {path.stem.replace('_', ' ')} area."
    if relative.startswith("app/pages/"):
        return f"Defines the legacy/component-level page adapter for {path.stem.replace('_', ' ')}; the production browser shell is served by app/web_app.py."
    if relative.startswith("services/"):
        return f"Implements the {path.stem.replace('_', ' ')} service used by the local WSP application."
    if relative.startswith("database/"):
        return f"Implements part of the local SQLite persistence layer: {path.stem.replace('_', ' ')}."
    if relative.startswith("scripts/"):
        return f"Provides the operational or development utility named {path.stem.replace('_', ' ')}."
    if relative.endswith("requirements.txt") or relative.endswith("requirements.lock.txt"):
        return "Declares the Python packages required to install and reproduce the WSP runtime."
    if relative.endswith("pyproject.toml"):
        return "Defines project metadata, supported Python version, dependencies, and pytest configuration."
    if relative.endswith("package-lock.json"):
        return "Records the JavaScript dependency lock state retained for repository reproducibility."
    if path.suffix.lower() == ".bat":
        return "Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow."
    if path.suffix.lower() == ".css":
        return "Defines visual styling used by the WSP user interface."
    if path.suffix.lower() in {".yml", ".yaml"}:
        return "Defines automated repository workflow configuration."
    if path.name == ".gitignore":
        return "Prevents machine-specific environments, models, databases, reports, and release outputs from entering source control."
    return f"Supports the WSP Offline System as the repository artifact `{relative}`."


def python_details(text: str) -> tuple[list[dict[str, object]], list[str], list[str]]:
    symbols: list[dict[str, object]] = []
    imports: list[str] = []
    routes: list[str] = []
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [{"kind": "parse note", "name": "Syntax error", "line": exc.lineno or 1, "summary": str(exc)}], [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "async function" if isinstance(node, ast.AsyncFunctionDef) else "function"
            summary = (ast.get_docstring(node) or "").strip().splitlines()
            signature = node.name
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [arg.arg for arg in node.args.posonlyargs + node.args.args]
                if node.args.vararg:
                    args.append(f"*{node.args.vararg.arg}")
                args.extend(arg.arg for arg in node.args.kwonlyargs)
                if node.args.kwarg:
                    args.append(f"**{node.args.kwarg.arg}")
                signature = f"{node.name}({', '.join(args)})"
            symbols.append({"kind": kind, "name": signature, "line": node.lineno, "summary": summary[0] if summary else "Implementation symbol."})
            for decorator in getattr(node, "decorator_list", []):
                rendered = ast.unparse(decorator) if hasattr(ast, "unparse") else ""
                if rendered.startswith("app."):
                    routes.append(rendered)
    return symbols, sorted(set(filter(None, imports))), routes


def js_details(text: str) -> tuple[list[dict[str, object]], list[str], list[str]]:
    symbols: list[dict[str, object]] = []
    for match in re.finditer(r"(?m)^(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)", text):
        line = text.count("\n", 0, match.start()) + 1
        symbols.append({"kind": "function", "name": f"{match.group(1)}({match.group(2).strip()})", "line": line, "summary": "Browser-side interaction or rendering function."})
    endpoints = sorted(set(re.findall(r"fetch\([`\"']([^`\"']+)", text)))
    browser_apis = []
    for api in ("localStorage", "sessionStorage", "fetch", "Chart", "FormData", "history", "navigator.clipboard"):
        if api in text:
            browser_apis.append(api)
    return symbols, browser_apis, endpoints


def powershell_details(text: str) -> tuple[list[dict[str, object]], list[str], list[str]]:
    symbols = []
    for match in re.finditer(r"(?mi)^function\s+([A-Za-z0-9_-]+)", text):
        symbols.append({"kind": "function", "name": match.group(1), "line": text.count("\n", 0, match.start()) + 1, "summary": "PowerShell workflow helper."})
    commands = sorted(set(re.findall(r"(?m)^\s*&?\s*([A-Za-z][A-Za-z0-9-]+)(?:\s|$)", text)))
    return symbols, commands[:30], []


def generic_details(path: Path, text: str) -> tuple[list[dict[str, object]], list[str], list[str]]:
    suffix = path.suffix.lower()
    if suffix == ".css":
        variables = re.findall(r"--([a-zA-Z0-9-]+)\s*:", text)
        selectors = re.findall(r"(?m)^([^@{}][^{}]+)\s*\{", text)
        symbols = [
            {"kind": "CSS selector", "name": selector.strip().replace("\n", " ")[:100], "line": text.count("\n", 0, text.find(selector)) + 1, "summary": "Visual rule."}
            for selector in selectors[:120]
        ]
        return symbols, [f"CSS custom property --{name}" for name in variables], []
    if suffix in {".yml", ".yaml"}:
        actions = sorted(set(re.findall(r"uses:\s*([^\s]+)", text)))
        jobs = re.findall(r"(?m)^\s{2}([\w-]+):\s*$", text)
        return [{"kind": "workflow job", "name": job, "line": 1, "summary": "GitHub Actions job."} for job in jobs], actions, []
    if suffix == ".bat":
        commands = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith(("@echo", "rem", "::"))]
        return [{"kind": "command", "name": command[:100], "line": index + 1, "summary": "Windows batch step."} for index, command in enumerate(commands[:40])], [], []
    if suffix == ".json":
        keys = re.findall(r'(?m)^\s*"([^"]+)"\s*:', text)
        return [{"kind": "configuration key", "name": key, "line": 1, "summary": "JSON configuration entry."} for key in list(dict.fromkeys(keys))[:80]], [], []
    if suffix == ".toml":
        sections = re.findall(r"(?m)^\[([^]]+)]", text)
        return [{"kind": "configuration section", "name": section, "line": 1, "summary": "TOML configuration section."} for section in sections], [], []
    return [], [], []


def analyze(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()
    if suffix in {".py", ".pyw"}:
        symbols, dependencies, endpoints = python_details(text)
    elif suffix == ".js" and path.name != "chart.umd.min.js":
        symbols, dependencies, endpoints = js_details(text)
    elif suffix == ".ps1":
        symbols, dependencies, endpoints = powershell_details(text)
    else:
        symbols, dependencies, endpoints = generic_details(path, text)
    return {
        "path": path,
        "relative": display_path(path),
        "purpose": purpose_for(path),
        "lines": text.count("\n") + (1 if text else 0),
        "symbols": symbols,
        "dependencies": dependencies,
        "endpoints": endpoints,
        "text": text,
    }


def local_module(path: Path) -> str | None:
    if path.suffix.lower() not in {".py", ".pyw"}:
        return None
    try:
        relative = path.relative_to(ROOT).with_suffix("")
    except ValueError:
        return None
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def relative_link(from_doc: Path, target: Path) -> str:
    return Path(__import__("os").path.relpath(target, from_doc.parent)).as_posix()


def write_reference_pages(items: list[dict[str, object]]) -> None:
    module_to_item = {module: item for item in items if (module := local_module(item["path"]))}
    dependents: dict[str, list[str]] = defaultdict(list)
    for item in items:
        for dependency in item["dependencies"]:
            for module in module_to_item:
                if dependency == module or dependency.startswith(f"{module}."):
                    dependents[module].append(item["relative"])

    for item in items:
        path = item["path"]
        output = doc_path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        source_link = relative_link(output, path)
        module = local_module(path)
        lines = [
            f"# `{item['relative']}`",
            "",
            f"[Open source]({source_link}) · [Code documentation index]({relative_link(output, DOCS_ROOT / 'CODE_REFERENCE.md')}) · [Feature and code flows]({relative_link(output, DOCS_ROOT / 'FEATURES_AND_CODE_FLOW.md')})",
            "",
            "## Responsibility",
            "",
            str(item["purpose"]),
            "",
            "## File facts",
            "",
            f"- **Type:** `{path.suffix.lower() or path.name}`",
            f"- **Size:** {item['lines']:,} lines",
            f"- **Layer:** `{item['relative'].split('/')[0]}`",
        ]
        if module:
            lines.append(f"- **Python module:** `{module}`")
        lines.extend(["", "## Dependencies and integration", ""])
        if item["dependencies"]:
            lines.extend(f"- `{dependency}`" for dependency in item["dependencies"][:80])
        else:
            lines.append("- No direct imports or external action dependencies were detected.")
        if module and dependents.get(module):
            lines.extend(["", "### Referenced by", ""])
            lines.extend(f"- `{dependent}`" for dependent in sorted(set(dependents[module])))
        if item["endpoints"]:
            lines.extend(["", "### Routes or endpoints", ""])
            lines.extend(f"- `{endpoint}`" for endpoint in item["endpoints"])
        lines.extend(["", "## Public symbols and executable sections", ""])
        if item["symbols"]:
            lines.extend(["| Line | Kind | Symbol | Role |", "|---:|---|---|---|"])
            for symbol in item["symbols"]:
                name = str(symbol["name"]).replace("|", "\\|").replace("\n", " ")
                summary = str(symbol["summary"]).replace("|", "\\|").replace("\n", " ")
                lines.append(f"| {symbol['line']} | {symbol['kind']} | `{name}` | {summary} |")
        else:
            lines.append("This file is declarative, a package marker, a dependency lock, or a vendored/static artifact and does not expose first-party callable symbols.")
        lines.extend(
            [
                "",
                "## Runtime flow",
                "",
                f"1. The application or development workflow loads `{item['relative']}` when its {item['relative'].split('/')[0]} responsibility is needed.",
                "2. Inputs are validated or normalized by the symbols/configuration listed above.",
                "3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.",
                "4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.",
                "",
                "## Maintenance notes",
                "",
                "- Keep behavior synchronized with the linked feature flow and automated tests.",
                "- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.",
                "- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.",
                "",
            ]
        )
        output.write_text("\n".join(lines), encoding="utf-8")


def write_index(items: list[dict[str, object]]) -> None:
    output = DOCS_ROOT / "CODE_REFERENCE.md"
    by_layer: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in items:
        by_layer[item["relative"].split("/")[0]].append(item)
    lines = [
        "# Complete code reference",
        "",
        "This is the generated source-level index for WSP Offline System. Every first-party source, test, installer, workflow, configuration, and dependency declaration has a dedicated Markdown page.",
        "",
        f"**Documented files:** {len(items)}",
        "",
        "[Documentation home](README.md) · [Feature and code flows](FEATURES_AND_CODE_FLOW.md) · [Architecture](ARCHITECTURE.md) · [User manual](USER_MANUAL.md)",
        "",
    ]
    for layer in sorted(by_layer):
        lines.extend([f"## `{layer}`", "", "| Source file | Responsibility | Lines |", "|---|---|---:|"])
        for item in sorted(by_layer[layer], key=lambda value: value["relative"].casefold()):
            link = relative_link(output, doc_path(item["path"]))
            lines.append(f"| [`{item['relative']}`]({link}) | {item['purpose']} | {item['lines']:,} |")
        lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    items = [analyze(path) for path in source_files()]
    REFERENCE_ROOT.mkdir(parents=True, exist_ok=True)
    write_reference_pages(items)
    write_index(items)
    print(f"Generated {len(items)} code reference pages under {REFERENCE_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
