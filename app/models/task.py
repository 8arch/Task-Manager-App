from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

from ..constants.enums import TaskStatus


@dataclass
class Task:
    """Модель задачи"""
    
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.NOT_DONE
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        """Валидация после инициализации."""
        self.title = self.title.strip()
        self.description = self.description.strip()

        if not self.title:
            raise ValueError("Название задачи не может быть пустым")

        if not isinstance(self.status, TaskStatus):
            raise ValueError("Неверный статус задачи")
        
        # Конвертация UUID в строку, если передан объект UUID
        if isinstance(self.id, UUID):
            self.id = str(self.id)

    def mark_done(self) -> None:
        """Отметить задачу как выполненную."""
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def mark_status(self, status: TaskStatus) -> None:
        """Изменить статус задачи."""
        if not isinstance(status, TaskStatus):
            raise ValueError("Неверный статус задачи")
        
        self.status = status
        self.updated_at = datetime.now().isoformat()
        
        if status == TaskStatus.DONE and not self.completed_at:
            self.completed_at = datetime.now().isoformat()
        elif status != TaskStatus.DONE:
            self.completed_at = None

    def update(self, title: Optional[str] = None, description: Optional[str] = None) -> None:
        """Обновить поля задачи."""
        if title is not None:
            self.title = title.strip()
            if not self.title:
                raise ValueError("Название задачи не может быть пустым")
        
        if description is not None:
            self.description = description.strip()
        
        self.updated_at = datetime.now().isoformat()

    def is_done(self) -> bool:
        """Проверить, выполнена ли задача."""
        return self.status == TaskStatus.DONE

    def to_dict(self) -> dict:
        """Преобразовать задачу в словарь для JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Создать задачу из словаря (из JSON)"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data["status"]),
            created_at=data["created_at"],
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
        )

    def __str__(self) -> str:
        """Строковое представление задачи"""
        status_icon = "✓" if self.is_done() else "○"
        return f"[{status_icon}] {self.title}"

    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Task(id={self.id[:8]}..., title='{self.title}', status={self.status.value})"

