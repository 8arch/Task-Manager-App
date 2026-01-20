"""
Task Manager - Приложение для управления задачами.

Точка входа в приложение.
"""

import sys
import logging
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.repositories.task_repository import TaskRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.task_service import TaskService
from app.services.workspace_service import WorkspaceService
from app.ui.console_ui import ConsoleUI
from app.constants.config import Config


def setup_logging() -> None:
    """Настроить систему логирования."""
    # Создаем директорию для логов
    Config.LOG_DIR.mkdir(exist_ok=True)
    
    # Настраиваем формат логирования
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            # Логи в файл
            logging.FileHandler(
                Config.LOG_DIR / Config.LOG_FILE,
                encoding='utf-8'
            ),
            # Логи в консоль (только WARNING и выше)
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Устанавливаем уровень для консоли
    console_handler = logging.getLogger().handlers[1]
    console_handler.setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info(f"Запуск {Config.APP_NAME} v{Config.VERSION}")
    logger.info("="*60)


def setup_directories() -> None:
    """Создать необходимые директории."""
    Config.DATA_DIR.mkdir(exist_ok=True)
    Config.LOG_DIR.mkdir(exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Директория данных: {Config.DATA_DIR}")
    logger.info(f"Директория логов: {Config.LOG_DIR}")


def initialize_repositories() -> tuple[TaskRepository, WorkspaceRepository]:
    """
    Инициализировать репозитории.
    
    Returns:
        Кортеж (TaskRepository, WorkspaceRepository)
    """
    logger = logging.getLogger(__name__)
    
    task_repository = TaskRepository(Config.DATA_DIR)
    workspace_repository = WorkspaceRepository(Config.DATA_DIR)
    
    logger.info("Репозитории инициализированы")
    
    return task_repository, workspace_repository


def initialize_services(
    task_repository: TaskRepository,
    workspace_repository: WorkspaceRepository
) -> tuple[TaskService, WorkspaceService]:
    """
    Инициализировать сервисы.
    
    Args:
        task_repository: Репозиторий задач
        workspace_repository: Репозиторий workspace
        
    Returns:
        Кортеж (TaskService, WorkspaceService)
    """
    logger = logging.getLogger(__name__)
    
    task_service = TaskService(task_repository)
    workspace_service = WorkspaceService(workspace_repository, task_repository)
    
    logger.info("Сервисы инициализированы")
    
    return task_service, workspace_service


def main() -> None:
    """Главная функция приложения."""
    logger = None
    
    try:
        # 1. Настраиваем логирование
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # 2. Создаем необходимые директории
        setup_directories()
        
        # 3. Инициализируем репозитории
        task_repository, workspace_repository = initialize_repositories()
        
        # 4. Инициализируем сервисы
        task_service, workspace_service = initialize_services(
            task_repository,
            workspace_repository
        )
        
        # 5. Создаем UI и запускаем приложение
        logger.info("Запуск пользовательского интерфейса")
        ui = ConsoleUI(task_service, workspace_service)
        ui.run()
        
        logger.info("Приложение завершено успешно")
        
    except KeyboardInterrupt:
        if logger:
            logger.info("Приложение прервано пользователем (Ctrl+C)")
        print("\n\nПриложение прервано пользователем.")
        sys.exit(0)
        
    except Exception as e:
        if logger:
            logger.critical(f"Критическая ошибка: {e}", exc_info=True)
        else:
            print(f"Критическая ошибка при запуске: {e}")
        
        print("\n" + "="*60)
        print("❌ КРИТИЧЕСКАЯ ОШИБКА")
        print("="*60)
        print(f"\n{e}\n")
        print("Подробности в логе:", Config.LOG_DIR / Config.LOG_FILE)
        print("="*60)
        
        sys.exit(1)


if __name__ == "__main__":
    main()