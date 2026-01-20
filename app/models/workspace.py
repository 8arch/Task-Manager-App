from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Workspace:
    
    name: str
    is_active: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        self.name = self.name.strip()
        
        if not self.name:
            raise ValueError("Имя пространства не может быть пустым")
        
        if isinstance(self.id, UUID):
            self.id = str(self.id)
    
    def update(self, name: Optional[str] = None, 
               is_active: Optional[bool] = None) -> None:
        if name is not None:
            self.name = name.strip()
            if not self.name:
                raise ValueError("Имя пространства не может быть пустым")
        
        
        if is_active is not None:
            self.is_active = is_active
        
        self.updated_at = datetime.now().isoformat()
    
    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now().isoformat()
    
    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Workspace":
        return cls(
            id=data["id"],
            name=data["name"],
            is_active=data.get("is_active", False),
            created_at=data["created_at"],
            updated_at=data.get("updated_at"),
        )
    
    def __str__(self) -> str:
        status = "●" if self.is_active else "○"
        return f"[{status}] {self.name}"
    
    def __repr__(self) -> str:
        return f"Workspace(id={self.id[:8]}..., name='{self.name}', is_active={self.is_active})"