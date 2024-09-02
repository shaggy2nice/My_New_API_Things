import json
import sys
from datetime import datetime, date, timedelta

class Task:
    def __init__(self, description, due_date=None, priority='Medium', status='In Progress'):
        self.description = description
        self.due_date = self.parse_due_date(due_date)
        self.priority = priority
        self.status = status

    def parse_due_date(self, due_date):
        if isinstance(due_date, str):
            try:
                return datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                return self._parse_relative_date(due_date)
        return due_date

    def _parse_relative_date(self, due_date_str):
        today = datetime.now().date()
        due_date_str = due_date_str.lower().strip()
        if due_date_str == 'today':
            return today
        elif due_date_str == 'tomorrow':
            return today + timedelta(days=1)
        elif due_date_str == 'next week':
            return today + timedelta(days=7)
        elif due_date_str == 'next month':
            next_month = today.replace(day=1) + timedelta(days=32)
            return next_month.replace(day=1)
        return None

    def __str__(self):
        return f"{self.description} (Due: {self.format_due_date()}, Priority: {self.priority}, Status: {self.status})"

    def format_due_date(self):
        if not self.due_date:
            return "No due date"
        today = datetime.now().date()
        if self.due_date == today:
            return "Today"
        elif self.due_date == today + timedelta(days=1):
            return "Tomorrow"
        else:
            return self.due_date.strftime("%Y-%m-%d")

    def is_overdue(self):
        return self.due_date and self.due_date < datetime.now().date()
    
    def due_within_one_day(self):
        today = datetime.now().date()
        return self.due_date and (self.due_date - today).days <= 1

def get_task_from_user():
    description = input("Enter the task description: ").strip()
    while True:
        due_date_str = input("Enter the due date (YYYY-MM-DD, today, tomorrow, next week, next month) or leave blank for no due date: ").strip()
        if not due_date_str:
            due_date = None
            break
        task = Task(description, due_date_str)
        if task.due_date is not None:
            due_date = task.due_date
            break
        else:
            print("Invalid date format. Please try again.")
    priority = input("Enter priority (High/Medium/Low): ").capitalize()
    if priority not in ["High", "Medium", "Low"]:
        priority = "Medium"
    status = input("Enter status (In Progress, On Hold, Complete): ").capitalize()
    if status not in ["In Progress", "On Hold", "Complete"]:
        status = "In Progress"
    return description, due_date, priority, status

def add_task(description, due_date, priority, status):
    task = Task(description, due_date, priority, status)
    tasks.append(task)
    print("Task added successfully!")

def remove_task():
    if not tasks:
        print("Your to-do list is empty.")
        return

    print("Your to-do list:")
    for index, task in enumerate(tasks, start=1):
        print(f"{index}. {task}")

    while True:
        try:
            task_index = int(input("Enter the number of the task you want to remove: ")) - 1
            if 0 <= task_index < len(tasks):
                removed_task = tasks.pop(task_index)
                print(f"Task removed: {removed_task}")
                break
            else:
                print("Invalid task number. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def update_task_status():
    if not tasks:
        print("Your to-do list is empty.")
        return

    print("Your to-do list:")
    for index, task in enumerate(tasks, start=1):
        print(f"{index}. {task}")

    while True:
        try:
            task_index = int(input("Enter the number of the task you want to update: ")) - 1
            if 0 <= task_index < len(tasks):
                new_status = input("Enter new status (In Progress, On Hold, Complete): ").capitalize()
                if new_status not in ["In Progress", "On Hold", "Complete"]:
                    print("Invalid status. Please try again.")
                    continue
                tasks[task_index].status = new_status
                if new_status == "Complete":
                    archived_tasks.append(tasks.pop(task_index))
                    print(f"Task archived: {archived_tasks[-1]}")
                else:
                    print(f"Task updated: {tasks[task_index]}")
                break
            else:
                print("Invalid task number. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

def supports_color():
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

def display_tasks():
    if tasks:
        print("Your to-do list:")
        for index, task in enumerate(tasks, start=1):
            task_str = f"{index}. {task}"
            if task.is_overdue():
                if supports_color():
                    print(f"{RED}{task_str} (OVERDUE){RESET}")
                else:
                    print(f"{task_str} (OVERDUE)")
            elif task.due_within_one_day():
                if supports_color():
                    print(f"{YELLOW}{task_str} (DUE SOON){RESET}")
                else:
                    print(f"{task_str} (DUE SOON)")
            else:
                print(task_str)
    else:
        print("Your to-do list is empty.")

def display_archived_tasks():
    if archived_tasks:
        print("Archived tasks:")
        for index, task in enumerate(archived_tasks, start=1):
            print(f"{index}. {task}")
    else:
        print("No archived tasks.")

def check_overdue_tasks():
    overdue_tasks = [task for task in tasks if task.is_overdue()]
    if overdue_tasks:
        print("\nOverdue tasks:")
        for task in overdue_tasks:
            print(f"{RED}- {task}{RESET}")
        print()

def save_tasks(tasks, filename='my_tasks.json'):
    with open(filename, 'w') as file:
        json.dump([{'description': task.description, 
                    'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None, 
                    'priority': task.priority,
                    'status': task.status} for task in tasks], file)

def load_tasks(filename='my_tasks.json'):
    try:
        with open(filename, 'r') as file:
            tasks_data = json.load(file)
            return [Task(**task) for task in tasks_data]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print('Error decoding JSON, returning empty task list. This may be caused by a corrupted file.')
        return []

def main():
    global tasks, archived_tasks
    tasks = load_tasks()  # Load tasks at the beginning
    archived_tasks = []  # Initialize archived tasks list
    
    check_overdue_tasks()  # Check for overdue tasks when starting the program
    
    while True:
        choice = input("Enter 'A' to add a task, 'R' to remove a task, 'U' to update task status, 'D' to display tasks, 'V' to view archived tasks, or 'Q' to quit: ").upper()
        if choice == 'A':
            description, due_date, priority, status = get_task_from_user()
            add_task(description, due_date, priority, status)
        elif choice == 'R':
            remove_task()
        elif choice == 'U':
            update_task_status()
        elif choice == 'D':
            display_tasks()
        elif choice == 'V':
            display_archived_tasks()
        elif choice == 'Q':
            save_tasks(tasks)  # Save tasks before quitting
            print("Tasks saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()