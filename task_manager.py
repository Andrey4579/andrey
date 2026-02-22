import customtkinter as ctk
import os
from datetime import datetime
from plyer import notification

# Класс отдельной задачи
class TaskItem(ctk.CTkFrame):
    def __init__(self, master, task_text, time_str, is_checked, save_callback, app):
        super().__init__(master, fg_color="transparent")
        self.save_callback = save_callback
        self.app = app

        # 1. Состояние чекбокса
        self.check_var = ctk.IntVar(value=1 if is_checked else 0)

        # 2. Контейнер для текста и даты
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="left", fill="both", expand=True)

        # 3. Чекбокс
        self.checkbox = ctk.CTkCheckBox(
            self.content_frame, 
            text=task_text, 
            variable=self.check_var,
            font=("Arial", 16), 
            command=self.update_style
        )
        self.checkbox.pack(side="top", anchor="w", padx=10, pady=(5, 0))

        # 4. Метка времени
        self.time_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Создано: {time_str}",
            font=("Arial", 10),
            text_color="gray"
        )
        self.time_label.pack(side="top", anchor="w", padx=45)

        # Применяем начальный стиль (если загружено как выполненное)
        self.update_style(notify=False)

    def update_style(self, notify=True):
        is_done = self.check_var.get() == 1
        
        # Смена цвета текста
        color = "gray" if is_done else ("white" if ctk.get_appearance_mode() == "Dark" else "black")
        self.checkbox.configure(text_color=color)

        # Уведомление только если галочку поставили вручную
        if is_done and notify:
            try:
                notification.notify(
                    title="Задача выполнена! ✅",
                    message=f"Вы завершили: {self.checkbox.cget('text')}",
                    app_name="Task Master",
                    timeout=2
                )
            except: pass

        # Сохраняем изменения в файл
        self.save_callback()

# Главное окно приложения
class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task Master Pro")
        self.geometry("500x600")
        self.db_file = "tasks.txt"
        
        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        # Заголовок
        self.label = ctk.CTkLabel(self, text="Менеджер задач", font=("Arial", 24, "bold"))
        self.label.pack(pady=20)

        # Поле ввода и кнопка Добавить
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=20)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Что нужно сделать?", width=300)
        self.entry.pack(side="left", padx=5)
        self.entry.bind("<Return>", lambda e: self.add_task())

        self.add_button = ctk.CTkButton(self.input_frame, text="Добавить", command=self.add_task)
        self.add_button.pack(side="left", padx=5)

        # Список задач (Scrollable Frame)
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Список дел")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Нижняя панель фильтров
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", padx=20, pady=10)

        self.filter_tab = ctk.CTkSegmentedButton(
            self.filter_frame, 
            values=["Все", "Активные", "Выполненные"],
            command=self.apply_filter
        )
        self.filter_tab.set("Все")
        self.filter_tab.pack(fill="x")

        # Кнопка Очистить с эффектами наведения
        self.clear_button = ctk.CTkButton(self, text="Очистить всё", fg_color="#7B241C", command=self.clear_tasks)
        self.clear_button.pack(pady=10)
        self.clear_button.bind("<Enter>", self.on_enter)
        self.clear_button.bind("<Leave>", self.on_leave)

    def add_task(self):
        task_text = self.entry.get().strip()
        if task_text:
            time_now = datetime.now().strftime("%d.%m %H:%M")
            self.add_task_to_ui(task_text, time_now)
            self.entry.delete(0, 'end')
            self.save_tasks()
            
            try:
                notification.notify(
                    title="Задача добавлена! ➕",
                    message=f"Вы добавили: {task_text}",
                    timeout=2
                )
            except: pass
        
    def add_task_to_ui(self, task, time_str, is_checked=False):
        item = TaskItem(self.scrollable_frame, task, time_str, is_checked, self.save_tasks, self)
        item.pack(fill="x", padx=5, pady=2)
        return item

    def save_tasks(self):
        with open(self.db_file, "w") as f:
            for widget in self.scrollable_frame.winfo_children():
                if isinstance(widget, TaskItem):
                    text = widget.checkbox.cget("text")
                    time = widget.time_label.cget("text").replace("Создано: ", "")
                    status = widget.check_var.get()
                    f.write(f"{text}|{time}|{status}\n")

    def load_tasks(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, "r") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 3:
                        # Важно: текст(0), время(1), статус(2)
                        self.add_task_to_ui(parts[0], parts[1], parts[2] == "1")

    def apply_filter(self, filter_name):
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, TaskItem):
                is_done = widget.check_var.get() == 1
                if filter_name == "Все" or \
                   (filter_name == "Выполненные" and is_done) or \
                   (filter_name == "Активные" and not is_done):
                    widget.pack(fill="x", padx=5, pady=2)
                else:
                    widget.pack_forget()

    def clear_tasks(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        self.on_leave(None)

    def on_enter(self, event):
        self.clear_button.configure(text="ТОЧНО УДАЛИТЬ?", fg_color="#E74C3C")

    def on_leave(self, event):
        self.clear_button.configure(text="Очистить всё", fg_color="#7B241C")

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()



# Что это даст:

    # Визуальный порядок: Пользователь видит, когда задача «зависла».
    # Профессиональный вид: Интерфейс становится более детализированным.
    # История: Если ты потом захочешь добавить сортировку, ты сможешь сортировать задачи «от старых к новым».

# Важный совет:
# Если ты хранишь задачи в текстовом файле (например, .txt или .json), 
# записывай их теперь строкой через разделитель, например:
# Купить хлеб|22.02 14:30|0 (текст | время | статус).
