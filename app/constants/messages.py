from typing import Final


class Messages:
    
    # Ошибки
    INVALID_DAY: Final[str] = "Некорректный день недели"
    EMPTY_TASK_LIST: Final[str] = "Список задач пуст"
    NO_TASKS_FOR_DAY: Final[str] = "Нет задач на этот день недели"
    INVALID_INPUT: Final[str] = "Некорректный ввод данных"
    TASK_NOT_FOUND: Final[str] = "Задача не найдена"
    
    # Успешные операции
    TASK_ADDED: Final[str] = "Задача успешно добавлена"
    TASK_REMOVED: Final[str] = "Задача успешно удалена"
    TASK_UPDATED: Final[str] = "Задача успешно обновлена"
    TASK_MARKED: Final[str] = "Задача отмечена как выполненная"
    
    # Предупреждения
    TASK_ALREADY_DONE: Final[str] = "Задача уже отмечена как выполненная"
    DUPLICATE_TASK: Final[str] = "Такая задача уже существует"
    
    # Промпты пользователя
    PROMPT_INPUT_DAY: Final[str] = "Введите день недели: "
    PROMPT_INPUT_TASK: Final[str] = "Введите описание задачи: "
    PROMPT_CHOOSE_ACTION: Final[str] = "Выберите действие: "
    PROMPT_CONFIRM: Final[str] = "Подтвердите действие (да/нет): "
