import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Task data structure
@dataclass
class Task:
    """Class to represent a task."""
    name: str
    task_type: str
    priority: int
    start_time: datetime
    end_time: datetime
    deadline: datetime

    def __str__(self):
        """Return a string representation of the task."""
        return f"Task: {self.name}, Type: {self.task_type}, Priority: {self.priority} - From {self.start_time:%H:%M} to {self.end_time:%H:%M}"

# Function to schedule tasks
def schedule_tasks(tasks, max_time):
    """Use dynamic programming to schedule tasks for maximum priority."""
    tasks.sort(key=lambda x: x.end_time)  # Sort by end time
    dp = [0] * (max_time + 1)  # Array to store max priorities
    for task in tasks:
        duration = round((task.end_time - task.start_time).total_seconds() / 3600)
        for i in range(max_time, duration - 1, -1):
            dp[i] = max(dp[i], dp[i - duration] + task.priority)  # Maximize priority
    return dp[max_time]

# QuickSort function for sorting tasks
def quick_sort(tasks):
    """Sort tasks using QuickSort."""
    if len(tasks) <= 1:
        return tasks
    pivot = tasks[len(tasks) // 2]  # Choose a pivot task
    left = [x for x in tasks if x < pivot]  # Tasks less than pivot
    middle = [x for x in tasks if x == pivot]  # Tasks equal to pivot
    right = [x for x in tasks if x > pivot]  # Tasks greater than pivot
    return quick_sort(left) + middle + quick_sort(right)  # Return sorted tasks

# Function to plot Gantt chart
def plot_gantt_chart(tasks):
    """Create and show a Gantt chart for tasks."""
    fig, ax = plt.subplots()  # Create figure
    for task in tasks:
        start = mdates.date2num(task.start_time)
        end = mdates.date2num(task.end_time)
        ax.barh(task.name, end - start, left=start, align='center')  # Add task bar
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Format time on x-axis
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Set hour intervals
    ax.set_xlim(mdates.dates2num(min(task.start_time for task in tasks)),
                mdates.date2num(max(task.end_time for task in tasks)))  # Set limits
    plt.xlabel("Time")
    plt.ylabel("Tasks")
    plt.title("Task Schedule Gantt Chart")
    plt.show()  # Show the chart

# Function to check reminders
def check_for_reminders(tasks, current_time):
    """Check for approaching or missed task deadlines."""
    for task in tasks:
        time_to_deadline = task.deadline - current_time
        if timedelta(minutes=0) <= time_to_deadline <= timedelta(hours=1):
            messagebox.showinfo("Reminder", f"Task '{task.name}' deadline is approaching!")  # Notify upcoming deadline
        elif time_to_deadline < timedelta(minutes=0):
            messagebox.showwarning("Missed Deadline", f"Task '{task.name}' has missed its deadline!")  # Warn missed deadline

# Main application class
class TaskSchedulerApp:
    def __init__(self, root):
        """Setup the main window and task list."""
        self.root = root
        self.root.title("Task Scheduler")  # Set title
        self.root.geometry("600x550")  # Set size
        self.root.configure(bg="#2c3e50")  # Set background color
        self.tasks = []  # Initialize task list

        self.create_widgets()  # Create GUI components

    def create_widgets(self):
        """Create and organize all GUI elements."""
        self.create_header()  # Add header
        self.create_form_inputs()  # Add input fields for tasks
        self.create_buttons()  # Add action buttons
        self.create_footer()  # Add footer

    def create_header(self):
        """Create header with title."""
        header_label = tk.Label(
            self.root,
            text="Task Scheduler",
            font=("Helvetica", 18, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        )
        header_label.pack(pady=15)  # Add padding

    def create_form_inputs(self):
        """Create input fields for entering task details."""
        input_frame = tk.Frame(self.root, bg="#2c3e50")  # Frame for inputs
        input_frame.pack(padx=20, pady=10, fill='x')  # Add padding

        # Labels and entry fields for task inputs
        labels = ["Task Name:", "Task Type:", "Priority:", "Start Time (HH:MM):", "End Time (HH:MM):", "Deadline (YYYY-MM-DD HH:MM):"]
        self.task_entries = []  # List to hold input fields

        for i, label in enumerate(labels):
            lbl = tk.Label(input_frame, text=label, font=("Helvetica", 12), fg="#ecf0f1", bg="#2c3e50")
            lbl.grid(row=i, column=0, sticky='e', padx=(0, 10), pady=5)  # Align labels to the right
            entry = tk.Entry(input_frame, font=("Helvetica", 12))  # Create entry field
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')  # Add entry to grid
            self.task_entries.append(entry)  # Store entry field

        # Task type dropdown
        self.task_type_var = tk.StringVar(value="Personal")  # Default value
        tk.OptionMenu(input_frame, self.task_type_var, "Personal", "Academic").grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # Priority dropdown
        self.priority_var = tk.IntVar(value=1)  # Default value
        tk.OptionMenu(input_frame, self.priority_var, *range(1, 6)).grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        # Configure column expansion
        input_frame.columnconfigure(1, weight=1)  # Make second column resizeable

    def create_buttons(self):
        """Create buttons for task management."""
        button_frame = tk.Frame(self.root, bg="#2c3e50")  # Frame for buttons
        button_frame.pack(pady=20)  # Add padding

        # Add task button
        tk.Button(
            button_frame,
            text="Add Task",
            font=("Helvetica", 12),
            fg="#ecf0f1",
            bg="#2980b9",
            command=self.add_task
        ).pack(side='left', padx=10)  # Add left

        # View Gantt chart button
        tk.Button(
            button_frame,
            text="View Gantt Chart",
            font=("Helvetica", 12),
            fg="#ecf0f1",
            bg="#2980b9",
            command=self.view_gantt_chart
        ).pack(side='left', padx=10)  # Add left

        # Check reminders button
        tk.Button(
            button_frame,
            text="Check Reminders",
            font=("Helvetica", 12),
            fg="#ecf0f1",
            bg="#e74c3c",
            command=self.check_reminders
        ).pack(side='left', padx=10)  # Add left

    def create_footer(self):
        """Create footer with copyright information."""
        footer_label = tk.Label(
            self.root,
            text="© 2023 Task Scheduler",
            font=("Helvetica", 10),
            fg="#bdc3c7",
            bg="#2c3e50"
        )
        footer_label.pack(side='bottom', pady=15)  # Add padding at the bottom

    def add_task(self):
        """Add a new task based on user input."""
        try:
            # Get task input
            name = self.task_entries[0].get()
            task_type = self.task_type_var.get()
            priority = self.priority_var.get()
            start_time = datetime.strptime(self.task_entries[3].get(), "%H:%M")  # Parse start time
            end_time = datetime.strptime(self.task_entries[4].get(), "%H:%M")  # Parse end time
            deadline = datetime.strptime(self.task_entries[5].get(), "%Y-%m-%d %H:%M")  # Parse deadline

            # Validate time
            if start_time >= end_time:
                raise ValueError("Start time must be before end time.")

            # Create and store task
            task = Task(name, task_type, priority, start_time, end_time, deadline)
            self.tasks.append(task)
            messagebox.showinfo("Task Added", f"Task '{name}' has been added!")  # Confirmation message
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))  # Show error for invalid input
        except Exception as e:
            messagebox.showerror("Error", "Please check your inputs.")  # General error message

    def view_gantt_chart(self):
        """Display tasks in a Gantt chart."""
        if self.tasks:
            sorted_tasks = quick_sort(self.tasks)  # Sort tasks
            plot_gantt_chart(sorted_tasks)  # Show Gantt chart
        else:
            messagebox.showinfo("No Tasks", "You need to add tasks to view the Gantt chart.")  # No tasks message

    def check_reminders(self):
        """Check for any task reminders."""
        current_time = datetime.now()  # Get current time
        check_for_reminders(self.tasks, current_time)  # Check reminders

# Main execution
if __name__ == "__main__":
    root = tk.Tk()  # Create the main window
    app = TaskSchedulerApp(root)  # Start the application
    root.mainloop()  # Run the GUI event loop