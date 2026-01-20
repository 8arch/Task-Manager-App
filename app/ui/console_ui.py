import logging
from typing import Optional

from app.services.task_service import TaskService
from app.services.workspace_service import WorkspaceService
from app.models.task import Task
from app.models.workspace import Workspace
from app.constants.enums import Day, TaskStatus
from app.constants.messages import Messages
from app.exceptions.custom_exceptions import (
    TaskManagerError,
    TaskNotFoundError,
    DuplicateTaskError
)


class ConsoleUI:
    """Консольный интерфейс для Task Manager."""
    
    def __init__(self, task_service: TaskService, workspace_service: WorkspaceService):
        """
        Инициализация UI.
        
        Args:
            task_service: Сервис управления задачами
            workspace_service: Сервис управления workspace
        """
        self.task_service = task_service
        self.workspace_service = workspace_service
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def run(self) -> None:
        """Запустить приложение."""
        print("\n" + "="*50)
        print("  Добро пожаловать в Task Manager!")
        print("="*50)
        
        try:
            # Загружаем все workspace
            self.workspace_service.load_all()
            
            # Проверяем, есть ли workspace
            if self.workspace_service.get_workspace_count() == 0:
                print("\n👋 Это ваш первый запуск!")
                print("У вас пока нет пространств задач.")
                
                create = input("\nСоздать новое пространство? (да/нет): ").strip().lower()
                if create in ["да", "yes", "y", ""]:
                    name = input("Введите название (Enter = 'Мои задачи'): ").strip()
                    if not name:
                        name = "Мои задачи"
                    
                    # description = input("Введите описание (Enter для пропуска): ").strip()
                    
                    active_ws = self.workspace_service.create_workspace(name)
                    self.workspace_service.set_active_workspace(active_ws.id)
                    print(f"\n✅ Создано пространство: {active_ws.name}")
                else:
                    print("\nСоздание пространства по умолчанию...")
                    active_ws = self.workspace_service.create_default_workspace()
                    print(f"✅ Создано пространство: {active_ws.name}")
            else:
                # Убеждаемся что есть активный workspace
                active_ws = self.workspace_service.ensure_active_workspace()
            
            # Загружаем задачи активного workspace
            self.task_service.load_workspace(active_ws.id)
            
            # Главный цикл
            while True:
                try:
                    self._show_main_menu()
                    choice = input("\nВыберите действие: ").strip()
                    
                    if choice == "0":
                        print("\nДо свидания!")
                        break
                    
                    self._handle_main_menu(choice)
                    
                except KeyboardInterrupt:
                    print("\n\nПрограмма прервана пользователем.")
                    break
                except Exception as e:
                    self.logger.error(f"Ошибка: {e}", exc_info=True)
                    print(f"\n❌ Произошла ошибка: {e}")
                    input("\nНажмите Enter для продолжения...")
        
        except Exception as e:
            self.logger.critical(f"Критическая ошибка: {e}", exc_info=True)
            print(f"\n❌ Критическая ошибка: {e}")
    
    def _show_main_menu(self) -> None:
        """Показать главное меню."""
        print("\n" + "="*50)
        active_ws = self.workspace_service.get_active_workspace()
        if active_ws:
            print(f"  Активный workspace: [{active_ws.name}]")
            task_count = self.task_service.get_task_count()
            done_count = self.task_service.get_done_tasks_count()
            print(f"  Задач: {task_count} (выполнено: {done_count})")
        print("="*50)
        print("\n1. Управление задачами")
        print("2. Управление workspace")
        print("3. Статистика")
        print("0. Выход")
    
    def _handle_main_menu(self, choice: str) -> None:
        """Обработать выбор главного меню."""
        actions = {
            "1": self._task_menu,
            "2": self._workspace_menu,
            "3": self._show_statistics,
        }
        
        action = actions.get(choice)
        if action:
            action()
        else:
            print("\n❌ Неверный выбор!")
    
    # ========== МЕНЮ ЗАДАЧ ==========
    
    def _task_menu(self) -> None:
        """Меню управления задачами."""
        while True:
            print("\n" + "-"*50)
            print("  УПРАВЛЕНИЕ ЗАДАЧАМИ")
            print("-"*50)
            print("\n1. Добавить задачу")
            print("2. Просмотреть задачи")
            print("3. Отметить задачу выполненной")
            print("4. Удалить задачу")
            print("5. Поиск задачи")
            print("6. Редактировать задачу")
            print("0. Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "0":
                break
            
            actions = {
                "1": self._add_task_flow,
                "2": self._view_tasks_flow,
                "3": self._mark_task_done_flow,
                "4": self._delete_task_flow,
                "5": self._search_task_flow,
                "6": self._edit_task_flow,
            }
            
            action = actions.get(choice)
            if action:
                action()
            else:
                print("\n❌ Неверный выбор!")
    
    def _add_task_flow(self) -> None:
        """Процесс добавления задачи."""
        print("\n--- Добавление задачи ---")
        
        # Выбор дня
        day = self._select_day()
        if not day:
            return
        
        # Ввод названия
        title = input("Введите название задачи: ").strip()
        if not title:
            print("❌ Название не может быть пустым!")
            return
        
        # Ввод описания (опционально)
        description = input("Введите описание (Enter для пропуска): ").strip()
        
        try:
            task = Task(title=title, description=description)
            self.task_service.add_task(day, task)
            print(f"\n✅ {Messages.TASK_ADDED}")
        except DuplicateTaskError:
            print(f"\n❌ {Messages.DUPLICATE_TASK}")
        except Exception as e:
            print(f"\n❌ Ошибка при добавлении: {e}")
    
    def _view_tasks_flow(self) -> None:
        """Процесс просмотра задач."""
        print("\n--- Просмотр задач ---")
        print("\n1. Показать все задачи")
        print("2. Показать задачи на конкретный день")
        
        choice = input("\nВыберите: ").strip()
        
        if choice == "1":
            self._show_all_tasks()
        elif choice == "2":
            day = self._select_day()
            if day:
                self._show_tasks_for_day(day)
        else:
            print("❌ Неверный выбор!")
    
    def _show_all_tasks(self) -> None:
        """Показать все задачи."""
        all_tasks = self.task_service.get_all_tasks()
        
        has_tasks = False
        for day in Day:
            tasks = all_tasks.get(day, [])
            if tasks:
                has_tasks = True
                print(f"\n📅 {day.value.capitalize()}:")
                for i, task in enumerate(tasks, 1):
                    status_icon = "✅" if task.is_done() else "⬜"
                    print(f"  {i}. {status_icon} {task.title}")
                    if task.description:
                        print(f"     └─ {task.description}")
        
        if not has_tasks:
            print("\n📭 Задач пока нет")
    
    def _show_tasks_for_day(self, day: Day) -> None:
        """Показать задачи на конкретный день."""
        tasks = self.task_service.get_tasks_for_day(day)
        
        print(f"\n📅 {day.value.capitalize()}:")
        
        if not tasks:
            print("  📭 Задач нет")
            return
        
        for i, task in enumerate(tasks, 1):
            status_icon = "✅" if task.is_done() else "⬜"
            print(f"  {i}. {status_icon} {task.title}")
            if task.description:
                print(f"     └─ {task.description}")
            print(f"     ID: {task.id[:8]}...")
    
    def _mark_task_done_flow(self) -> None:
        """Процесс отметки задачи выполненной."""
        print("\n--- Отметить задачу выполненной ---")
        
        task_id = input("Введите ID задачи (или название для поиска): ").strip()
        
        if not task_id:
            print("❌ ID не может быть пустым!")
            return
        
        try:
            # Пробуем найти по ID
            task = self.task_service.get_task_by_id(task_id)
            
            # Если не найдено по ID, ищем по названию
            if not task:
                tasks = self.task_service.find_by_name(task_id)
                if not tasks:
                    print(f"❌ {Messages.TASK_NOT_FOUND}")
                    return
                elif len(tasks) == 1:
                    task = tasks[0]
                else:
                    # Несколько задач с таким названием
                    print("\nНайдено несколько задач:")
                    for i, t in enumerate(tasks, 1):
                        print(f"{i}. {t.title} (ID: {t.id[:8]}...)")
                    
                    idx = input("\nВыберите номер задачи: ").strip()
                    try:
                        task = tasks[int(idx) - 1]
                    except (ValueError, IndexError):
                        print("❌ Неверный номер!")
                        return
            
            if task.is_done():
                print(f"\n⚠️ {Messages.TASK_ALREADY_DONE}")
                return
            
            self.task_service.mark_task_done(task.id)
            print(f"\n✅ {Messages.TASK_MARKED}")
            
        except TaskNotFoundError:
            print(f"\n❌ {Messages.TASK_NOT_FOUND}")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
    
    def _delete_task_flow(self) -> None:
        """Процесс удаления задачи."""
        print("\n--- Удаление задачи ---")
        
        task_id = input("Введите ID задачи (или название): ").strip()
        
        if not task_id:
            print("❌ ID не может быть пустым!")
            return
        
        try:
            # Находим задачу (аналогично mark_task_done_flow)
            task = self.task_service.get_task_by_id(task_id)
            
            if not task:
                tasks = self.task_service.find_by_name(task_id)
                if not tasks:
                    print(f"❌ {Messages.TASK_NOT_FOUND}")
                    return
                elif len(tasks) == 1:
                    task = tasks[0]
                else:
                    print("\nНайдено несколько задач:")
                    for i, t in enumerate(tasks, 1):
                        print(f"{i}. {t.title}")
                    
                    idx = input("\nВыберите номер: ").strip()
                    try:
                        task = tasks[int(idx) - 1]
                    except (ValueError, IndexError):
                        print("❌ Неверный номер!")
                        return
            
            # Подтверждение
            confirm = input(f"\nУдалить задачу '{task.title}'? (да/нет): ").strip().lower()
            if confirm not in ["да", "yes", "y"]:
                print("Отменено")
                return
            
            self.task_service.remove_task(task.id)
            print(f"\n✅ {Messages.TASK_REMOVED}")
            
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
    
    def _search_task_flow(self) -> None:
        """Процесс поиска задачи."""
        print("\n--- Поиск задачи ---")
        
        query = input("Введите название задачи: ").strip()
        
        if not query:
            print("❌ Запрос не может быть пустым!")
            return
        
        tasks = self.task_service.find_by_name(query)
        
        if not tasks:
            print(f"\n❌ Задачи не найдены")
            return
        
        print(f"\n✅ Найдено задач: {len(tasks)}")
        for task in tasks:
            status_icon = "✅" if task.is_done() else "⬜"
            print(f"\n{status_icon} {task.title}")
            if task.description:
                print(f"  └─ {task.description}")
            print(f"  ID: {task.id[:8]}...")
            print(f"  Создано: {task.created_at}")
    
    def _edit_task_flow(self) -> None:
        """Процесс редактирования задачи."""
        print("\n--- Редактирование задачи ---")
        
        task_id = input("Введите ID задачи: ").strip()
        task = self.task_service.get_task_by_id(task_id)
        
        if not task:
            print(f"❌ {Messages.TASK_NOT_FOUND}")
            return
        
        print(f"\nТекущие данные:")
        print(f"Название: {task.title}")
        print(f"Описание: {task.description or '(нет)'}")
        
        new_title = input("\nНовое название (Enter для пропуска): ").strip()
        new_desc = input("Новое описание (Enter для пропуска): ").strip()
        
        if new_title or new_desc:
            self.task_service.update_task(
                task.id,
                title=new_title if new_title else None,
                description=new_desc if new_desc else None
            )
            print(f"\n✅ {Messages.TASK_UPDATED}")
        else:
            print("\nНичего не изменено")
    
    # ========== МЕНЮ WORKSPACE ==========
    
    def _workspace_menu(self) -> None:
        """Меню управления workspace."""
        while True:
            print("\n" + "-"*50)
            print("  УПРАВЛЕНИЕ WORKSPACE")
            print("-"*50)
            print("\n1. Создать workspace")
            print("2. Переключить workspace")
            print("3. Удалить workspace")
            print("4. Список workspace")
            print("0. Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "0":
                break
            
            actions = {
                "1": self._create_workspace_flow,
                "2": self._switch_workspace_flow,
                "3": self._delete_workspace_flow,
                "4": self._list_workspaces,
            }
            
            action = actions.get(choice)
            if action:
                action()
            else:
                print("\n❌ Неверный выбор!")
    
    def _create_workspace_flow(self) -> None:
        """Процесс создания workspace."""
        print("\n--- Создание workspace ---")
        
        name = input("Введите название: ").strip()
        if not name:
            print("❌ Название не может быть пустым!")
            return
        
        # description = input("Введите описание (Enter для пропуска): ").strip()
        
        try:
            workspace = self.workspace_service.create_workspace(name)
            print(f"\n✅ Workspace создан: {workspace.name}")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
    
    def _switch_workspace_flow(self) -> None:
        """Процесс переключения workspace."""
        print("\n--- Переключение workspace ---")
        
        workspaces = self.workspace_service.get_all_workspaces()
        
        if not workspaces:
            print("❌ Нет доступных workspace")
            return
        
        print("\nДоступные workspace:")
        for i, ws in enumerate(workspaces, 1):
            active = "●" if ws.is_active else "○"
            print(f"{i}. {active} {ws.name}")
        
        choice = input("\nВыберите номер: ").strip()
        
        try:
            idx = int(choice) - 1
            workspace = workspaces[idx]
            
            self.workspace_service.set_active_workspace(workspace.id)
            self.task_service.load_workspace(workspace.id)
            
            print(f"\n✅ Переключено на: {workspace.name}")
        except (ValueError, IndexError):
            print("❌ Неверный номер!")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
    
    def _delete_workspace_flow(self) -> None:
        """Процесс удаления workspace."""
        print("\n--- Удаление workspace ---")
        
        workspaces = self.workspace_service.get_all_workspaces()
        
        if not workspaces:
            print("❌ Нет workspace для удаления")
            return
        
        if len(workspaces) == 1:
            print("❌ Нельзя удалить единственный workspace!")
            return
        
        print("\nДоступные workspace:")
        for i, ws in enumerate(workspaces, 1):
            print(f"{i}. {ws.name}")
        
        choice = input("\nВыберите номер: ").strip()
        
        try:
            idx = int(choice) - 1
            workspace = workspaces[idx]
            
            confirm = input(f"\nУдалить workspace '{workspace.name}' и все его задачи? (да/нет): ").strip().lower()
            if confirm not in ["да", "yes", "y"]:
                print("Отменено")
                return
            
            self.workspace_service.delete_workspace(workspace.id)
            
            # Переключаемся на другой workspace
            active = self.workspace_service.ensure_active_workspace()
            self.task_service.load_workspace(active.id)
            
            print(f"\n✅ Workspace удален")
            
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
    
    def _list_workspaces(self) -> None:
        """Показать список workspace."""
        workspaces = self.workspace_service.get_all_workspaces()
        
        if not workspaces:
            print("\n❌ Нет workspace")
            return
        
        print("\n" + "="*50)
        print("  СПИСОК WORKSPACE")
        print("="*50)
        
        for ws in workspaces:
            active = "●" if ws.is_active else "○"
            print(f"\n{active} {ws.name}")
            if ws.description:
                print(f"  └─ {ws.description}")
            print(f"  ID: {ws.id[:8]}...")
            print(f"  Создан: {ws.created_at}")
    
    # ========== СТАТИСТИКА ==========
    
    def _show_statistics(self) -> None:
        """Показать статистику."""
        print("\n" + "="*50)
        print("  СТАТИСТИКА")
        print("="*50)
        
        # Статистика по задачам
        total_tasks = self.task_service.get_task_count()
        done_tasks = self.task_service.get_done_tasks_count()
        pending_tasks = total_tasks - done_tasks
        
        print(f"\n📊 Задачи:")
        print(f"  Всего: {total_tasks}")
        print(f"  Выполнено: {done_tasks}")
        print(f"  В работе: {pending_tasks}")
        
        if total_tasks > 0:
            completion_rate = (done_tasks / total_tasks) * 100
            print(f"  Прогресс: {completion_rate:.1f}%")
        
        # Статистика по дням
        print(f"\n📅 По дням:")
        all_tasks = self.task_service.get_all_tasks()
        for day in Day:
            tasks = all_tasks.get(day, [])
            if tasks:
                done = sum(1 for t in tasks if t.is_done())
                print(f"  {day.value.capitalize()}: {len(tasks)} (✅ {done})")
        
        # Статистика по workspace
        ws_count = self.workspace_service.get_workspace_count()
        active_ws = self.workspace_service.get_active_workspace()
        
        print(f"\n🗂️  Workspace:")
        print(f"  Всего: {ws_count}")
        print(f"  Активный: {active_ws.name if active_ws else 'Нет'}")
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    def _select_day(self) -> Optional[Day]:
        """Выбрать день недели."""
        print("\nВыберите день недели:")
        for i, day in enumerate(Day, 1):
            print(f"{i}. {day.value.capitalize()}")
        
        choice = input("\nВведите номер: ").strip()
        
        try:
            idx = int(choice) - 1
            return list(Day)[idx]
        except (ValueError, IndexError):
            print("❌ Неверный номер!")
            return None