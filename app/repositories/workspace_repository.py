from pathlib import Path
from typing import List, Optional
import logging

from app.repositories.base_repository import BaseRepository
from app.models.workspace import Workspace
from app.exceptions.custom_exceptions import TaskManagerError


class WorkspaceRepository(BaseRepository):
    """Репозиторий для работы с пространствами задач."""
    
    WORKSPACES_FILE = "workspaces.json"
    
    def __init__(self, data_dir: Path):
        """
        Инициализация репозитория workspace.
        
        Args:
            data_dir: Директория для хранения данных
        """
        super().__init__(data_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def save(self, workspaces: List[Workspace]) -> None:
        """
        Сохранить все workspace.
        
        Args:
            workspaces: Список всех workspace
        """
        file_path = self._get_file_path(self.WORKSPACES_FILE)
        
        # Создаем backup перед сохранением
        self._create_backup(file_path)
        
        # Конвертируем в формат для JSON
        data = [workspace.to_dict() for workspace in workspaces]
        
        self._write_json(file_path, data)
        self.logger.info(f"Сохранено {len(workspaces)} workspace")
    
    def load(self) -> List[Workspace]:
        """
        Загрузить все workspace.
        
        Returns:
            Список всех workspace
        """
        file_path = self._get_file_path(self.WORKSPACES_FILE)
        
        # Читаем данные из JSON
        data = self._read_json(file_path)
        
        # Если файл не существует, возвращаем пустой список
        if data is None:
            self.logger.info("Файл workspaces не найден, создаем пустой список")
            return []
        
        # Конвертируем из JSON в Workspace объекты
        workspaces = [Workspace.from_dict(ws_dict) for ws_dict in data]
        
        self.logger.info(f"Загружено {len(workspaces)} workspace")
        return workspaces
    
    def save_workspace(self, workspace: Workspace) -> None:
        """
        Сохранить один workspace (добавить или обновить).
        
        Args:
            workspace: Workspace для сохранения
        """
        workspaces = self.load()
        
        # Ищем существующий workspace с таким ID
        existing_index = None
        for i, ws in enumerate(workspaces):
            if ws.id == workspace.id:
                existing_index = i
                break
        
        # Обновляем или добавляем
        if existing_index is not None:
            workspaces[existing_index] = workspace
            self.logger.info(f"Workspace обновлен: {workspace.name}")
        else:
            workspaces.append(workspace)
            self.logger.info(f"Workspace добавлен: {workspace.name}")
        
        # Сохраняем весь список
        self.save(workspaces)
    
    def delete_workspace(self, workspace_id: str) -> bool:
        """
        Удалить workspace по ID.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            True, если workspace был удален
        """
        workspaces = self.load()
        original_count = len(workspaces)
        
        # Фильтруем список, удаляя нужный workspace
        workspaces = [ws for ws in workspaces if ws.id != workspace_id]
        
        if len(workspaces) < original_count:
            self.save(workspaces)
            self.logger.info(f"Workspace удален: {workspace_id}")
            return True
        
        self.logger.warning(f"Workspace не найден для удаления: {workspace_id}")
        return False
    
    def get_workspace_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """
        Получить workspace по ID.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            Workspace или None
        """
        workspaces = self.load()
        
        for ws in workspaces:
            if ws.id == workspace_id:
                return ws
        
        return None
    
    def get_active_workspace(self) -> Optional[Workspace]:
        """
        Получить активный workspace.
        
        Returns:
            Активный workspace или None
        """
        workspaces = self.load()
        
        for ws in workspaces:
            if ws.is_active:
                return ws
        
        return None
    
    def set_active_workspace(self, workspace_id: str) -> bool:
        """
        Установить workspace как активный (деактивируя остальные).
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            True, если успешно
        """
        workspaces = self.load()
        found = False
        
        # Деактивируем все workspace
        for ws in workspaces:
            if ws.id == workspace_id:
                ws.activate()
                found = True
            else:
                ws.deactivate()
        
        if found:
            self.save(workspaces)
            self.logger.info(f"Workspace активирован: {workspace_id}")
            return True
        
        self.logger.warning(f"Workspace не найден для активации: {workspace_id}")
        return False
    
    def workspace_exists(self, workspace_id: str) -> bool:
        """
        Проверить существование workspace.
        
        Args:
            workspace_id: ID workspace
            
        Returns:
            True, если workspace существует
        """
        return self.get_workspace_by_id(workspace_id) is not None
    
    def get_workspace_count(self) -> int:
        """
        Получить количество workspace.
        
        Returns:
            Количество workspace
        """
        workspaces = self.load()
        return len(workspaces)
        
        
    