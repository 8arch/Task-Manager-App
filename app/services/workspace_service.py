from typing import List, Optional, Dict
import logging

from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.task_repository import TaskRepository
from app.models.workspace import Workspace
from app.constants.messages import Messages
from app.exceptions.custom_exceptions import (
    TaskManagerError,
    EmptyTaskListError
)


class WorkspaceService:
    """Сервис для управления пространствами задач."""
    
    def __init__(self, workspace_repository: WorkspaceRepository, 
                 task_repository: TaskRepository):
        """
        Инициализация сервиса workspace.
        
        Args:
            workspace_repository: Репозиторий для работы с workspace
            task_repository: Репозиторий для работы с задачами (для удаления)
        """
        self._workspace_repository = workspace_repository
        self._task_repository = task_repository
        
        # Хранилище workspace в памяти
        self._workspaces: Dict[str, Workspace] = {}
        self._active_workspace_id: Optional[str] = None
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_all(self) -> None:
        """Загрузить все workspace из JSON."""
        self.logger.info("Загрузка всех workspace")
        
        workspaces = self._workspace_repository.load()

        # Строим словарь для быстрого доступа
        self._workspaces.clear()
        self._active_workspace_id = None
        
        for ws in workspaces:
            self._workspaces[ws.id] = ws
            if ws.is_active:
                self._active_workspace_id = ws.id
        
        self.logger.info(f"Загружено {len(workspaces)} workspace")
    
    def create_workspace(self, name: str) -> Workspace:
        """
        Создать новый workspace.
        
        Args:
            name: Название workspace
        Returns:
            Созданный workspace
        """
        workspace = Workspace(
            name=name,
            is_active=False
        )
        
        # Добавляем в память
        self._workspaces[workspace.id] = workspace
        
        # Сохраняем в JSON
        self._workspace_repository.save_workspace(workspace)
        
        self.logger.info(f"Создан workspace: {workspace.name} (ID: {workspace.id})")
        return workspace
    
    def delete_workspace(self, workspace_id: str) -> None:
        """
        Удалить workspace и все его задачи.
        
        Args:
            workspace_id: ID workspace
            
        Raises:
            TaskManagerError: Если workspace не найден
        """
        if workspace_id not in self._workspaces:
            raise TaskManagerError(f"Workspace не найден: {workspace_id}")
        
        workspace = self._workspaces[workspace_id]
        
        # Удаляем из памяти
        del self._workspaces[workspace_id]
        
        # Если это был активный workspace, сбрасываем
        if self._active_workspace_id == workspace_id:
            self._active_workspace_id = None
        
        # Удаляем из JSON
        self._workspace_repository.delete_workspace(workspace_id)
        
        # Удаляем все задачи workspace
        self._task_repository.delete_workspace_tasks(workspace_id)
        
        self.logger.info(f"Удален workspace: {workspace.name} (ID: {workspace_id})")
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """
        Получить workspace по ID.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            Workspace или None
        """
        return self._workspaces.get(workspace_id)
    
    def get_all_workspaces(self) -> List[Workspace]:
        """
        Получить все workspace.
        
        Returns:
            Список всех workspace
        """
        return list(self._workspaces.values())
    
    def set_active_workspace(self, workspace_id: str) -> None:
        """
        Установить workspace как активный.
        
        Args:
            workspace_id: ID workspace
            
        Raises:
            TaskManagerError: Если workspace не найден
        """
        if workspace_id not in self._workspaces:
            raise TaskManagerError(f"Workspace не найден: {workspace_id}")
        
        # Деактивируем все workspace
        for ws in self._workspaces.values():
            ws.deactivate()
        
        # Активируем выбранный
        workspace = self._workspaces[workspace_id]
        workspace.activate()
        self._active_workspace_id = workspace_id
        
        # Сохраняем изменения
        self._workspace_repository.save(list(self._workspaces.values()))
        
        self.logger.info(f"Активирован workspace: {workspace.name}")
    
    def get_active_workspace(self) -> Optional[Workspace]:
        """
        Получить активный workspace.
        
        Returns:
            Активный workspace или None
        """
        if self._active_workspace_id:
            return self._workspaces.get(self._active_workspace_id)
        return None
    
    def get_active_workspace_id(self) -> Optional[str]:
        """
        Получить ID активного workspace.
        
        Returns:
            ID активного workspace или None
        """
        return self._active_workspace_id
    
    def update_workspace(self, workspace_id: str, name: Optional[str] = None) -> None:
        """
        Обновить workspace.
        
        Args:
            workspace_id: ID workspace
            name: Новое название
            
        Raises:
            TaskManagerError: Если workspace не найден
        """
        if workspace_id not in self._workspaces:
            raise TaskManagerError(f"Workspace не найден: {workspace_id}")
        
        workspace = self._workspaces[workspace_id]
        workspace.update(name=name)
        
        # Сохраняем
        self._workspace_repository.save_workspace(workspace)
        
        self.logger.info(f"Обновлен workspace: {workspace.name}")
    
    def workspace_exists(self, workspace_id: str) -> bool:
        """
        Проверить существование workspace.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            True, если workspace существует
        """
        return workspace_id in self._workspaces
    
    def get_workspace_count(self) -> int:
        """
        Получить количество workspace.
        
        Returns:
            Количество workspace
        """
        return len(self._workspaces)
    
    def has_active_workspace(self) -> bool:
        """
        Проверить наличие активного workspace.
        
        Returns:
            True, если есть активный workspace
        """
        return self._active_workspace_id is not None
    
    def get_workspace_by_name(self, name: str) -> Optional[Workspace]:
        """
        Найти workspace по имени.
        
        Args:
            name: Название workspace
            
        Returns:
            Workspace или None
        """
        name_lower = name.lower().strip()
        for ws in self._workspaces.values():
            if ws.name.lower().strip() == name_lower:
                return ws
        return None
    
    def create_default_workspace(self) -> Workspace:
        """
        Создать workspace по умолчанию.
        
        Returns:
            Созданный workspace
        """
        workspace = self.create_workspace(
            name="Мои задачи",
        )
        
        # Делаем его активным
        self.set_active_workspace(workspace.id)
        
        self.logger.info("Создан workspace по умолчанию")
        return workspace
    
    def ensure_active_workspace(self) -> Workspace:
        """
        Убедиться, что есть активный workspace (создать если нет).
        
        Returns:
            Активный workspace
        """
        active = self.get_active_workspace()
        
        if active is None:
            # Если нет активного, пытаемся активировать первый
            workspaces = self.get_all_workspaces()
            if workspaces:
                self.set_active_workspace(workspaces[0].id)
                return workspaces[0]
            else:
                # Если нет workspace вообще, создаем дефолтный
                return self.create_default_workspace()
        
        return active