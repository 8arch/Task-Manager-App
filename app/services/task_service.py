
from typing import List, Optional, Dict
import logging

from app.repositories.task_repository import TaskRepository
from app.models.task import Task
from app.constants.enums import Day, TaskStatus
from app.constants.messages import Messages
from app.exceptions.custom_exceptions import (
    TaskNotFoundError,
    EmptyTaskListError,
    DuplicateTaskError
)


class TaskService:
    """Сервис для управления задачами."""
    
    def __init__(self, task_repository: TaskRepository):
        """
        Инициализация сервиса задач.
        
        Args:
            task_repository: Репозиторий для работы с задачами
        """
        self._task_repository = task_repository
        self._current_workspace_id: Optional[str] = None
        
        # Хранилище задач в памяти
        self._tasks_by_day: Dict[Day, List[Task]] = {day: [] for day in Day}
        
        # Индексы для быстрого поиска O(1)
        self._task_by_id: Dict[str, Task] = {}
        self._task_by_name: Dict[str, List[str]] = {}  # {name.lower(): [task_ids]}
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_workspace(self, workspace_id: str) -> None:
        """
        Загрузить задачи workspace и построить индексы.
        
        Args:
            workspace_id: ID workspace
        """
        self.logger.info(f"Загрузка workspace: {workspace_id}")
        
        # Загружаем задачи из JSON
        self._tasks_by_day = self._task_repository.load(workspace_id)
        self._current_workspace_id = workspace_id
        
        # Очищаем и строим индексы
        self._rebuild_indexes()
        
        task_count = sum(len(tasks) for tasks in self._tasks_by_day.values())
        self.logger.info(f"Загружено {task_count} задач для workspace {workspace_id}")
    
    def _rebuild_indexes(self) -> None:
        """Перестроить все индексы."""
        self._task_by_id.clear()
        self._task_by_name.clear()
        
        for day, tasks in self._tasks_by_day.items():
            for task in tasks:
                # Индекс по ID
                self._task_by_id[task.id] = task
                
                # Индекс по имени
                name_key = task.title.lower().strip()
                if name_key not in self._task_by_name:
                    self._task_by_name[name_key] = []
                self._task_by_name[name_key].append(task.id)
    
    def _save_current_workspace(self) -> None:
        """Сохранить текущее состояние задач в JSON."""
        if self._current_workspace_id is None:
            raise ValueError("Workspace не загружен")
        
        self._task_repository.save(self._current_workspace_id, self._tasks_by_day)
    
    def add_task(self, day: Day, task: Task) -> None:
        """
        Добавить задачу.
        
        Args:
            day: День недели
            task: Задача
            
        Raises:
            DuplicateTaskError: Если задача с таким именем уже существует в этот день
        """
        # Проверка на дубликат в этом дне
        name_key = task.title.lower().strip()
        if self._has_task_on_day(day, name_key):
            raise DuplicateTaskError(Messages.DUPLICATE_TASK)
        
        # Добавляем в список дня
        self._tasks_by_day[day].append(task)
        
        # Обновляем индексы
        self._task_by_id[task.id] = task
        if name_key not in self._task_by_name:
            self._task_by_name[name_key] = []
        self._task_by_name[name_key].append(task.id)
        
        # Сохраняем
        self._save_current_workspace()
        self.logger.info(f"Задача добавлена: {task.title} на {day.value}")
    
    def _has_task_on_day(self, day: Day, name_key: str) -> bool:
        """Проверить наличие задачи с таким именем в конкретный день."""
        for task in self._tasks_by_day[day]:
            if task.title.lower().strip() == name_key:
                return True
        return False
    
    def remove_task(self, task_id: str) -> None:
        """
        Удалить задачу по ID.
        
        Args:
            task_id: ID задачи
            
        Raises:
            TaskNotFoundError: Если задача не найдена
        """
        task = self._task_by_id.get(task_id)
        if not task:
            raise TaskNotFoundError(Messages.TASK_NOT_FOUND)
        
        # Находим и удаляем из списка дня
        for day, tasks in self._tasks_by_day.items():
            if task in tasks:
                tasks.remove(task)
                break
        
        # Удаляем из индексов
        del self._task_by_id[task_id]
        
        name_key = task.title.lower().strip()
        if name_key in self._task_by_name:
            self._task_by_name[name_key].remove(task_id)
            if not self._task_by_name[name_key]:
                del self._task_by_name[name_key]
        
        # Сохраняем
        self._save_current_workspace()
        self.logger.info(f"Задача удалена: {task.title}")
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Получить задачу по ID - O(1).
        
        Args:
            task_id: ID задачи
            
        Returns:
            Task или None
        """
        return self._task_by_id.get(task_id)
    
    def find_by_name(self, name: str) -> List[Task]:
        """
        Найти задачи по имени - O(1).
        
        Args:
            name: Название задачи
            
        Returns:
            Список задач с таким именем
        """
        name_key = name.lower().strip()
        task_ids = self._task_by_name.get(name_key, [])
        return [self._task_by_id[tid] for tid in task_ids]
    
    def get_tasks_for_day(self, day: Day) -> List[Task]:
        """
        Получить все задачи на день.
        
        Args:
            day: День недели
            
        Returns:
            Список задач
        """
        return self._tasks_by_day.get(day, [])
    
    def get_all_tasks(self) -> Dict[Day, List[Task]]:
        """
        Получить все задачи, сгруппированные по дням.
        
        Returns:
            Словарь {Day: [Task, ...]}
        """
        return self._tasks_by_day.copy()
    
    def mark_task_done(self, task_id: str) -> None:
        """
        Отметить задачу как выполненную.
        
        Args:
            task_id: ID задачи
            
        Raises:
            TaskNotFoundError: Если задача не найдена
        """
        task = self._task_by_id.get(task_id)
        if not task:
            raise TaskNotFoundError(Messages.TASK_NOT_FOUND)
        
        task.mark_done()
        
        # Сохраняем
        self._save_current_workspace()
        self.logger.info(f"Задача отмечена как выполненная: {task.title}")
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """
        Изменить статус задачи.
        
        Args:
            task_id: ID задачи
            status: Новый статус
            
        Raises:
            TaskNotFoundError: Если задача не найдена
        """
        task = self._task_by_id.get(task_id)
        if not task:
            raise TaskNotFoundError(Messages.TASK_NOT_FOUND)
        
        task.mark_status(status)
        
        # Сохраняем
        self._save_current_workspace()
        self.logger.info(f"Статус задачи изменен: {task.title} -> {status.value}")
    
    def update_task(self, task_id: str, title: Optional[str] = None, 
                   description: Optional[str] = None) -> None:
        """
        Обновить задачу.
        
        Args:
            task_id: ID задачи
            title: Новое название
            description: Новое описание
            
        Raises:
            TaskNotFoundError: Если задача не найдена
        """
        task = self._task_by_id.get(task_id)
        if not task:
            raise TaskNotFoundError(Messages.TASK_NOT_FOUND)
        
        # Если меняется название, нужно обновить индекс
        old_name_key = task.title.lower().strip()
        
        task.update(title=title, description=description)
        
        # Обновляем индекс имен, если название изменилось
        if title is not None:
            new_name_key = task.title.lower().strip()
            if old_name_key != new_name_key:
                # Удаляем из старого ключа
                if old_name_key in self._task_by_name:
                    self._task_by_name[old_name_key].remove(task_id)
                    if not self._task_by_name[old_name_key]:
                        del self._task_by_name[old_name_key]
                
                # Добавляем в новый ключ
                if new_name_key not in self._task_by_name:
                    self._task_by_name[new_name_key] = []
                self._task_by_name[new_name_key].append(task_id)
        
        # Сохраняем
        self._save_current_workspace()
        self.logger.info(f"Задача обновлена: {task.title}")
    
    def get_task_count(self) -> int:
        """
        Получить общее количество задач.
        
        Returns:
            Количество задач
        """
        return len(self._task_by_id)
    
    def get_done_tasks_count(self) -> int:
        """
        Получить количество выполненных задач.
        
        Returns:
            Количество выполненных задач
        """
        return sum(1 for task in self._task_by_id.values() if task.is_done())
    
    def clear_workspace(self) -> None:
        """Очистить все задачи текущего workspace."""
        self._tasks_by_day = {day: [] for day in Day}
        self._task_by_id.clear()
        self._task_by_name.clear()
        
        self._save_current_workspace()
        self.logger.info("Все задачи очищены")