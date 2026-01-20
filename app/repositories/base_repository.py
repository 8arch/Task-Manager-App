import json
import logging
from pathlib import Path
from typing import Any, Optional
from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """Базовый класс для всех репозиториев."""
    
    def __init__(self, data_dir: Path):
        """
        Инициализация репозитория.
        
        Args:
            data_dir: Директория для хранения данных
        """
        self.data_dir = data_dir
        self.logger = logging.getLogger(self.__class__.__name__)
        self._ensure_data_dir()
    
    def _ensure_data_dir(self) -> None:
        """Создать директорию для данных, если она не существует."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Директория данных проверена: {self.data_dir}")
        except Exception as e:
            self.logger.error(f"Ошибка создания директории {self.data_dir}: {e}")
            raise
    
    def _get_file_path(self, filename: str) -> Path:
        """
        Получить полный путь к файлу.
        
        Args:
            filename: Имя файла
            
        Returns:
            Полный путь к файлу
        """
        return self.data_dir / filename
    
    def _read_json(self, file_path: Path) -> Optional[dict]:
        """
        Прочитать данные из JSON файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Данные из файла или None, если файл не существует
        """
        if not file_path.exists():
            self.logger.warning(f"Файл не найден: {file_path}")
            return None
        
        try:
            # Проверяем, не пустой ли файл
            if file_path.stat().st_size == 0:
                self.logger.warning(f"Файл пуст: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.logger.debug(f"Данные прочитаны из {file_path}")
                return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка декодирования JSON из {file_path}: {e}")
            self.logger.warning(f"Файл будет считаться пустым: {file_path}")
            # Не пробрасываем исключение, возвращаем None
            return None
        except Exception as e:
            self.logger.error(f"Ошибка чтения файла {file_path}: {e}")
            raise
    
    def _write_json(self, file_path: Path, data: Any, indent: int = 2) -> None:
        """
        Записать данные в JSON файл.
        
        Args:
            file_path: Путь к файлу
            data: Данные для записи
            indent: Отступы для форматирования JSON
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
                self.logger.debug(f"Данные записаны в {file_path}")
        except Exception as e:
            self.logger.error(f"Ошибка записи в файл {file_path}: {e}")
            raise
    
    def _delete_file(self, file_path: Path) -> bool:
        """
        Удалить файл.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True, если файл удален, False если файла не было
        """
        if not file_path.exists():
            self.logger.warning(f"Файл для удаления не найден: {file_path}")
            return False
        
        try:
            file_path.unlink()
            self.logger.info(f"Файл удален: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка удаления файла {file_path}: {e}")
            raise
    
    def _file_exists(self, filename: str) -> bool:
        """
        Проверить существование файла.
        
        Args:
            filename: Имя файла
            
        Returns:
            True, если файл существует
        """
        file_path = self._get_file_path(filename)
        return file_path.exists()
    
    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Создать резервную копию файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Путь к backup файлу или None
        """
        if not file_path.exists():
            return None
        
        try:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            backup_path.write_bytes(file_path.read_bytes())
            self.logger.debug(f"Создана резервная копия: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Ошибка создания backup: {e}")
            return None
    
    @abstractmethod
    def save(self, *args, **kwargs) -> None:
        """Сохранить данные (должен быть переопределен в наследниках)."""
        pass
    
    @abstractmethod
    def load(self, *args, **kwargs) -> Any:
        """Загрузить данные (должен быть переопределен в наследниках)."""
        pass