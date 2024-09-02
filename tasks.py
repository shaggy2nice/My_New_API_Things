tasks = set()

def add_task(task):
    if task in tasks:
        print("Task already exists!")
    else:
        tasks.add(task)
        print("Task added successfully!")

def remove_task(task):
    if task in tasks:
        tasks.remove(task)
        print("Task removed successfully!")
    else:
        print("Task not found.")

def display_tasks():
    if tasks:
        print("Your to-do list:")
        for index, task in enumerate(tasks, start=1):
            print(f"{index}. {task}")
    else:
        print("Your to-do list is empty.")

# Function to take user input for adding a task
def get_task_from_user():
    while True:
        task = input("Enter the task: ").strip()
        if task:
            return task
        print("Task cannot be empty. Please try again.")

# Function to take user input for removing a task
def get_task_to_remove():
    return input("Enter the task to remove: ")

# Function to take user input for displaying tasks
def get_display_choice():
    return input("Enter 'A' to add a task, 'R' to remove a task, 'D' to display tasks, or 'Q' to quit: ").upper()

def main():
    while True:
        choice = get_display_choice()
        if choice == 'Q':
            print("Goodbye!")
            break

def main():
    while True:
        choice = get_display_choice()
        if choice == 'A':
            task = get_task_from_user()
            add_task(task)
        elif choice == 'R':
            task = get_task_to_remove()
            remove_task(task)
        elif choice == 'D':
            display_tasks()
        elif choice == 'Q':
            print("Goodbye!")
            break    
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()