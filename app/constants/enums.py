from enum import Enum


class Day(Enum):
    MONDAY =    "понедельник"
    TUESDAY =   "вторник"
    WEDNESDAY = "среда"
    THURSDAY =  "четверг"
    FRIDAY =    "пятница"
    SATURDAY =  "суббота"
    SUNDAY =    "воскресенье"
    
    @classmethod
    def from_string(cls, day_str: str) -> 'Day':
        """Получить день по строковому значению."""
        for day in cls:
            if day.value.lower() == day_str.lower():
                return day
        raise ValueError(f"Неизвестный день: {day_str}")


class TaskStatus(Enum):
    DONE =     "выполнено"
    NOT_DONE = "не выполнено"
    
    def __str__(self) -> str:
        return self.value

