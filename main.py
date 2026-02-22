import customtkinter as ctk
import os

# Настройка темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Имя файла для хранения данных
DB_FILE = "tasks.txt"

# Разберем каждую строку кода, чтобы понимать, как данные превращаются в интерфейс и обратно.



# 3. Как работает загрузка данных             

def load_tasks():
    """Загружает задачи из файла при старте"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                # 1. Убираем лишние пробелы и разбиваем строку по символу "|"
                # Из "Помыть кота|1" получаем список ["Помыть кота", "1"]
                parts = line.strip().split("|")

                # Проверяем, что в строке реально есть обе части
                if len(parts) == 2:
                    task_text, status = parts

                    # 2. Вызываем функцию отрисовки
                    # Выражение (status == "1") превратит строку в True или False
                    add_task_to_ui(task_text, is_checked=(status == "1"))
def toggle_task_style(checkbox):
    """Меняет цвет текста в зависимости от галочки"""
    if checkbox.get() == 1:
        checkbox.configure(text_color="gray")
    else:
        checkbox.configure(text_color="white")   
    save_tasks() # Заодно сохраняем состояние в файл
         
# 1. Как работает создание галочки(UI)

def add_task_to_ui(task, is_checked=False):
    """Создает чекбокс для задачи в списке"""
    # 1. Создаем "умную" переменную Python, которая умеет хранить целое число(0 или 1)
    # Мы ставим ей значение 1, если задача загружена как выполненная (is_checked=True)
    check_var = ctk.IntVar(value=1 if is_checked else 0)
  


    # 2. Создаем чекбокс вместо текстовой метки
    checkbox = ctk.CTkCheckBox(
        scrollable_frame,
        text=task,
        variable=check_var,
        font=("Arial", 16),
        command=save_tasks # Сохраняем состояние при каждом клике
    )

    # Теперь настраиваем команду (передаем сам созданный checkbox в функцию стиля)
    checkbox.configure(command=lambda: toggle_task_style(checkbox))

    # Сразу задаем цвет при загрузке из файла
    toggle_task_style(checkbox)

    # 3. Выводим на экран
    checkbox.pack(pady=5, padx=10, anchor="w")

    # Главный секрет здесь: variable=check_var.
    # Теперь, когда ты нажимаешь на галочку, значение внутри check_var 
    # само меняется с 0 на 1 (и наоборот)
    # Тебе не нужно писать код для смены состояния, библиотека делает это за тебя.

# --------------------------------------------------------------------

# 2. Как работает сохранение в файл

def save_tasks():
    """Сохраняет задачи и их статусы (выполнено или нет)"""   
    with open(DB_FILE, "w", encoding="utf-8") as f:
        # Перебираем все элементы, которые мы "напаковали" в скролл-панель
        for widget in scrollable_frame.winfo_children():
            # Проверяем: точно ли этот виджет - наша галочка? (защита от ошибок)
            if isinstance(widget, ctk.CTkCheckBox):
                task_text = widget.cget("text") # Берем текст из виджета
                # Получаем значение переменной чекбокса(1 или 0)
                status = widget.get() # Берем состояние (0 или 1)

                # Записываем строку в формате: Помыть кота|1
                f.write(f"{task_text}|{status}\n")

# Зачем нувжен формат Текст|Статус?
# Если записывать просто текст, при следующем запуске программа не узнает,
# была ли задача выполнена.
# Разделитель | позволяет нам "склеить" два разных типа данных в одну строку.
# 
# ----------------------------------------------------------------------------


                

def add_task():
    task = entry.get()
    if task:
        add_task_to_ui(task)
        entry.delete(0, 'end')
        save_tasks() # Сохраняем изменения

def clear_tasks():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE) # Удаляем файл, если список пуст

app = ctk.CTk()
app.geometry("500x550")
app.title("Task Master v1.2")

label = ctk.CTkLabel(app, text="Менеджер задач", font=("Arial", 24, "bold"))
label.pack(pady=15)

input_frame = ctk.CTkFrame(app)
input_frame.pack(pady=10, padx=20, fill="x")

entry = ctk.CTkEntry(input_frame, placeholder_text="Что нужно сделать?", width=280)
entry.pack(side="left", padx=10, pady=10)

add_button = ctk.CTkButton(input_frame, text="Добавить", width=100, command=add_task)
add_button.pack(side="left", padx=5)

scrollable_frame = ctk.CTkScrollableFrame(app, label_text="Список дел", width=450, height=300)
scrollable_frame.pack(pady=10, padx=20, fill="both", expand=True)

# 1. Функции-обработчики (они просто лежат в памяти и ждут вызова)
def on_enter(event):
    clear_button.configure(text="ТОЧНО УДАЛИТЬ?", fg_color="#E74C3C")

def on_leave(event):
    clear_button.configure(text="Очистить всё", fg_color="#7B241C") 

    
# 2. Создаем саму кнопку
clear_button = ctk.CTkButton(
    app, 
    text="Очистить всё", 
    fg_color="#7B241C", 
    hover_color="#E74C3C", 
    command=clear_tasks
)
clear_button.pack(pady=15)

# 3. А теперь ПРИВЯЗЫВАЕМ функции к событиям этой кнопки
# Эти строки должны быть отдельно, не внутри других функций!
clear_button.bind("<Enter>", on_enter)  
clear_button.bind("<Leave>", on_leave) 

# Загружаем задачи перед запуском основного цикла
load_tasks()

# Привязываем клавишу Enter (Return) ко всему окну приложения
app.bind("<Return>", lambda event: add_task())


app.mainloop()


                                                                   
