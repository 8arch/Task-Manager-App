
class TaskManagerError(Exception):
    """Базовое исключение для всех ошибок Task Manager."""
    
    def __init__(self, message: str = "Произошла ошибка в Task Manager"):
        self.message = message
        super().__init__(self.message)


# ============================================================================
# ИСКЛЮЧЕНИЯ ДЛЯ ЗАДАЧ
# ============================================================================

class TaskError(TaskManagerError):
    """Базовое исключение для ошибок задач."""
    pass


class TaskNotFoundError(TaskError):
    """Задача не найдена."""
    
    def __init__(self, task_id: str = None):
        if task_id:
            message = f"Задача с ID '{task_id}' не найдена"
        else:
            message = "Задача не найдена"
        super().__init__(message)


class DuplicateTaskError(TaskError):
    """Задача с таким названием уже существует."""
    
    def __init__(self, task_name: str = None):
        if task_name:
            message = f"Задача '{task_name}' уже существует"
        else:
            message = "Такая задача уже существует"
        super().__init__(message)


class InvalidTaskError(TaskError):
    """Некорректные данные задачи."""
    
    def __init__(self, reason: str = "Некорректные данные задачи"):
        super().__init__(reason)


# ============================================================================
# ИСКЛЮЧЕНИЯ ДЛЯ WORKSPACE
# ============================================================================

class WorkspaceError(TaskManagerError):
    """Базовое исключение для ошибок workspace."""
    pass


class WorkspaceNotFoundError(WorkspaceError):
    """Workspace не найден."""
    
    def __init__(self, workspace_id: str = None):
        if workspace_id:
            message = f"Workspace с ID '{workspace_id}' не найден"
        else:
            message = "Workspace не найден"
        super().__init__(message)


class DuplicateWorkspaceError(WorkspaceError):
    """Workspace с таким названием уже существует."""
    
    def __init__(self, workspace_name: str = None):
        if workspace_name:
            message = f"Workspace '{workspace_name}' уже существует"
        else:
            message = "Такой workspace уже существует"
        super().__init__(message)


class InvalidWorkspaceError(WorkspaceError):
    """Некорректные данные workspace."""
    
    def __init__(self, reason: str = "Некорректные данные workspace"):
        super().__init__(reason)


class NoActiveWorkspaceError(WorkspaceError):
    """Нет активного workspace."""
    
    def __init__(self):
        super().__init__("Нет активного workspace")


class CannotDeleteLastWorkspaceError(WorkspaceError):
    """Нельзя удалить последний workspace."""
    
    def __init__(self):
        super().__init__("Нельзя удалить единственный workspace")


# ============================================================================
# ИСКЛЮЧЕНИЯ ВАЛИДАЦИИ
# ============================================================================

class ValidationError(TaskManagerError):
    """Базовое исключение для ошибок валидации."""
    pass


class EmptyTaskListError(ValidationError):
    """Список задач пуст."""
    
    def __init__(self):
        super().__init__("Список задач пуст")


class InvalidDayError(ValidationError):
    """Некорректный день недели."""
    
    def __init__(self, day: str = None):
        if day:
            message = f"Некорректный день недели: '{day}'"
        else:
            message = "Некорректный день недели"
        super().__init__(message)


class InvalidInputError(ValidationError):
    """Некорректный ввод данных."""
    
    def __init__(self, reason: str = "Некорректный ввод данных"):
        super().__init__(reason)


class EmptyFieldError(ValidationError):
    """Обязательное поле пустое."""
    
    def __init__(self, field_name: str):
        super().__init__(f"Поле '{field_name}' не может быть пустым")


# ============================================================================
# ИСКЛЮЧЕНИЯ ХРАНИЛИЩА
# ============================================================================

class StorageError(TaskManagerError):
    """Базовое исключение для ошибок хранилища."""
    pass


class FileReadError(StorageError):
    """Ошибка чтения файла."""
    
    def __init__(self, file_path: str, reason: str = None):
        message = f"Не удалось прочитать файл: {file_path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


class FileWriteError(StorageError):
    """Ошибка записи в файл."""
    
    def __init__(self, file_path: str, reason: str = None):
        message = f"Не удалось записать в файл: {file_path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


class FileNotFoundError(StorageError):
    """Файл не найден."""
    
    def __init__(self, file_path: str):
        super().__init__(f"Файл не найден: {file_path}")


class InvalidJSONError(StorageError):
    """Некорректный формат JSON."""
    
    def __init__(self, file_path: str, reason: str = None):
        message = f"Некорректный JSON в файле: {file_path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def get_exception_hierarchy() -> str:
    """
    Получить строковое представление иерархии исключений.
    
    Returns:
        Строка с иерархией исключений
    """
    return """
Иерархия исключений Task Manager:

TaskManagerError
├── TaskError
│   ├── TaskNotFoundError
│   ├── DuplicateTaskError
│   └── InvalidTaskError
├── WorkspaceError
│   ├── WorkspaceNotFoundError
│   ├── DuplicateWorkspaceError
│   ├── InvalidWorkspaceError
│   ├── NoActiveWorkspaceError
│   └── CannotDeleteLastWorkspaceError
├── ValidationError
│   ├── EmptyTaskListError
│   ├── InvalidDayError
│   ├── InvalidInputError
│   └── EmptyFieldError
└── StorageError
    ├── FileReadError
    ├── FileWriteError
    ├── FileNotFoundError
    └── InvalidJSONError
    """