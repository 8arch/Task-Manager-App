from typing import Final
from pathlib import Path


class Config:

    # Пути
    BASE_DIR: Final[Path] = Path(__file__).parent.parent
    DATA_DIR: Final[Path] = BASE_DIR / "data"
    LOG_DIR: Final[Path] = BASE_DIR / "logs"
    
    # Файлы
    LOG_FILE: Final[str] = "app.log"
    
    # Настройки приложения
    APP_NAME: Final[str] = "Task Manager"
    VERSION: Final[str] = "Beta"
    MAX_TASK_LENGTH: Final[int] = 200
    DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
    
    # Логирование
    LOG_LEVEL: Final[str] = "INFO"
    LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"