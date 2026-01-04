import uuid

class Task:
    def __init__(self, title, description=""):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.completed = False

    def __repr__(self):
        status = "Completed" if self.completed else "Pending"
        return f"ID: {self.id[:8]}... | Title: {self.title} | Status: {status}"

class TaskManager:
    def __init__(self):
        self.tasks = {}

    def add_task(self, title, description=""):
        if not title:
            return "Task title cannot be empty."
        task = Task(title, description)
        self.tasks[task.id] = task
        return f"Task '{task.title}' added with ID: {task.id[:8]}..."

    def view_tasks(self, status="all"):
        filtered_tasks = []
        for task_id in self.tasks:
            task = self.tasks[task_id]
            if status == "all" or \
               (status == "pending" and not task.completed) or \
               (status == "completed" and task.completed):
                filtered_tasks.append(task)

        if not filtered_tasks:
            return "No tasks found."
        
        return "\n".join([str(task) for task in filtered_tasks])

    def update_task(self, task_id_prefix, new_title=None, new_description=None):
        task = self._find_task_by_prefix(task_id_prefix)
        if not task:
            return f"Task with ID prefix '{task_id_prefix}' not found."

        if new_title:
            task.title = new_title
        if new_description is not None: # Allow empty string to clear description
            task.description = new_description
        return f"Task '{task.title}' (ID: {task.id[:8]}...) updated."

    def delete_task(self, task_id_prefix):
        task = self._find_task_by_prefix(task_id_prefix)
        if not task:
            return f"Task with ID prefix '{task_id_prefix}' not found."
        
        del self.tasks[task.id]
        return f"Task '{task.title}' (ID: {task.id[:8]}...) deleted."

    def mark_task_complete(self, task_id_prefix, complete=True):
        task = self._find_task_by_prefix(task_id_prefix)
        if not task:
            return f"Task with ID prefix '{task_id_prefix}' not found."
        
        task.completed = complete
        status = "completed" if complete else "pending"
        return f"Task '{task.title}' (ID: {task.id[:8]}...) marked as {status}."

    def _find_task_by_prefix(self, task_id_prefix):
        # Find task by partial ID match
        for task_id, task in self.tasks.items():
            if task_id.startswith(task_id_prefix):
                return task
        return None

def display_menu():
    print("\n--- Todo App Menu ---")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete")
    print("6. Mark Task Pending")
    print("7. Exit")
    print("---------------------")

def main():
    manager = TaskManager()

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            title = input("Enter task title: ")
            description = input("Enter task description (optional): ")
            print(manager.add_task(title, description))
        elif choice == '2':
            status_filter = input("View (all/pending/completed)? [all]: ").lower() or "all"
            print(manager.view_tasks(status_filter))
        elif choice == '3':
            task_id_prefix = input("Enter task ID prefix to update: ")
            new_title = input("Enter new title (leave blank to keep current): ")
            new_description = input("Enter new description (leave blank to keep current, type 'CLEAR' to remove): ")
            if new_description == "CLEAR":
                new_description = ""
            elif new_description == "":
                new_description = None
            
            print(manager.update_task(task_id_prefix, new_title if new_title else None, new_description))
        elif choice == '4':
            task_id_prefix = input("Enter task ID prefix to delete: ")
            print(manager.delete_task(task_id_prefix))
        elif choice == '5':
            task_id_prefix = input("Enter task ID prefix to mark complete: ")
            print(manager.mark_task_complete(task_id_prefix))
        elif choice == '6':
            task_id_prefix = input("Enter task ID prefix to mark pending: ")
            print(manager.mark_task_complete(task_id_prefix, complete=False))
        elif choice == '7':
            print("Exiting Todo App. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()