from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SUPPORTED_RUNTIME = "Python 3.11+"
VALID_RUNTIME_MODES = {"development", "testing", "production"}
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppSettings:
    app_name: str = "WSP Offline System"
    project_root: Path = PROJECT_ROOT
    data_dir: Path | None = None
    runtime_mode: str = "development"
    native_mode: bool = False
    ui_host: str = "127.0.0.1"
    ui_port: int = 8080
    semantic_search_enabled: bool = True
    embedding_model_name: str = "mixedbread-ai/mxbai-embed-large-v1"
    embedding_local_files_only: bool = True
    semantic_vector_store_backend: str = "faiss"
    rag_candidate_limit: int = 60
    rag_profile_text_limit: int = 180
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_name: str = "gemma3:4b"
    ollama_request_timeout_seconds: float = 90.0

    def __post_init__(self) -> None:
        project_root = Path(self.project_root).resolve()
        data_dir = Path(self.data_dir).resolve() if self.data_dir else project_root / "data"

        if self.runtime_mode not in VALID_RUNTIME_MODES:
            valid = ", ".join(sorted(VALID_RUNTIME_MODES))
            raise ValueError(f"Invalid runtime_mode {self.runtime_mode!r}. Expected one of: {valid}")

        object.__setattr__(self, "project_root", project_root)
        object.__setattr__(self, "data_dir", data_dir)

    @property
    def database_path(self) -> Path:
        return self.data_dir / "wsp.db"

    @property
    def incoming_excel_dir(self) -> Path:
        if self.runtime_mode == "testing":
            return self.data_dir / "import_folder"
        return self.project_root.parent / "Import Folder"

    @property
    def import_folder_archive_dir(self) -> Path:
        return self.incoming_excel_dir / "archive"

    @property
    def import_folder_config_path(self) -> Path:
        return self.data_dir / "import_folder_config.json"

    @property
    def archive_dir(self) -> Path:
        return self.data_dir / "archive"

    @property
    def original_excel_archive_dir(self) -> Path:
        return self.archive_dir / "original_excels"

    @property
    def backup_dir(self) -> Path:
        return self.data_dir / "backups"

    @property
    def export_dir(self) -> Path:
        return self.data_dir / "exports"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def semantic_index_dir(self) -> Path:
        return self.data_dir / "semantic_index"

    @property
    def required_directories(self) -> tuple[Path, ...]:
        return (
            self.data_dir,
            self.incoming_excel_dir,
            self.import_folder_archive_dir,
            self.archive_dir,
            self.original_excel_archive_dir,
            self.backup_dir,
            self.export_dir,
            self.logs_dir,
            self.semantic_index_dir,
        )


def get_default_settings() -> AppSettings:
    return AppSettings()


def get_testing_settings(data_dir: Path) -> AppSettings:
    return AppSettings(data_dir=data_dir, runtime_mode="testing")


def ensure_data_directories(settings: AppSettings) -> tuple[Path, ...]:
    for directory in settings.required_directories:
        if directory.exists() and not directory.is_dir():
            raise NotADirectoryError(f"Configured data path exists but is not a directory: {directory}")
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        if not existed:
            LOGGER.info("Created data directory: %s", directory)
    return settings.required_directories
