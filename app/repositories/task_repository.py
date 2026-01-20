from pathlib import Path
from typing import Dict, List, Optional
import logging

from app.repositories.base_repository import BaseRepository
from app.models.task import Task
from app.constants.enums import Day
from app.exceptions.custom_exceptions import TaskNotFoundError


class TaskRepository(BaseRepository):
    """Репозиторий для работы с задачами."""
    
    def __init__(self, data_dir: Path):
        """
        Инициализация репозитория задач.
        
        Args:
            data_dir: Директория для хранения файлов задач
        """
        # Создаем поддиректорию для задач
        tasks_dir = data_dir / "tasks"
        super().__init__(tasks_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _get_workspace_filename(self, workspace_id: str) -> str:
        """
        Получить имя файла для workspace.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            Имя файла
        """
        return f"{workspace_id}.json"
    
    def save(self, workspace_id: str, tasks_by_day: Dict[Day, List[Task]]) -> None:
        """
        Сохранить все задачи workspace.
        
        Args:
            workspace_id: ID workspace
            tasks_by_day: Словарь {Day: [Task, Task, ...]}
        """
        filename = self._get_workspace_filename(workspace_id)
        file_path = self._get_file_path(filename)
        
        # Создаем backup перед сохранением
        self._create_backup(file_path)
        
        # Конвертируем в формат для JSON
        data = {}
        for day, tasks in tasks_by_day.items():
            # Ключ - строковое значение дня (например, "понедельник")
            day_key = day.value
            data[day_key] = [task.to_dict() for task in tasks]
        
        self._write_json(file_path, data)
        self.logger.info(f"Задачи сохранены для workspace {workspace_id}")
    
    def load(self, workspace_id: str) -> Dict[Day, List[Task]]:
        """
        Загрузить все задачи workspace.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            Словарь {Day: [Task, Task, ...]}
        """
        filename = self._get_workspace_filename(workspace_id)
        file_path = self._get_file_path(filename)
        
        # Читаем данные из JSON
        data = self._read_json(file_path)
        
        # Если файл не существует, возвращаем пустую структуру
        if data is None:
            self.logger.info(f"Файл задач для workspace {workspace_id} не найден, создаем новый")
            return {day: [] for day in Day}
        
        # Конвертируем из JSON в Task объекты
        tasks_by_day = {}
        for day_str, tasks_data in data.items():
            # Находим соответствующий Day enum
            day = Day(day_str)
            tasks = [Task.from_dict(task_dict) for task_dict in tasks_data]
            tasks_by_day[day] = tasks
        
        # Добавляем пустые списки для дней без задач
        for day in Day:
            if day not in tasks_by_day:
                tasks_by_day[day] = []
        
        self.logger.info(f"Загружено задач для workspace {workspace_id}: "
                        f"{sum(len(tasks) for tasks in tasks_by_day.values())}")
        return tasks_by_day
    
    def load_tasks_for_day(self, workspace_id: str, day: Day) -> List[Task]:
        """
        Загрузить задачи для конкретного дня.
        
        Args:
            workspace_id: ID workspace
            day: День недели
            
        Returns:
            Список задач
        """
        all_tasks = self.load(workspace_id)
        return all_tasks.get(day, [])
    
    def delete_workspace_tasks(self, workspace_id: str) -> bool:
        """
        Удалить все задачи workspace.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            True, если задачи удалены
        """
        filename = self._get_workspace_filename(workspace_id)
        file_path = self._get_file_path(filename)
        
        result = self._delete_file(file_path)
        if result:
            self.logger.info(f"Задачи workspace {workspace_id} удалены")
        return result
    
    def workspace_exists(self, workspace_id: str) -> bool:
        """
        Проверить существование файла задач для workspace.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            True, если файл существует
        """
        filename = self._get_workspace_filename(workspace_id)
        return self._file_exists(filename)
    
    def get_task_count(self, workspace_id: str) -> int:
        """
        Получить общее количество задач в workspace.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            Количество задач
        """
        tasks_by_day = self.load(workspace_id)
        return sum(len(tasks) for tasks in tasks_by_day.values())