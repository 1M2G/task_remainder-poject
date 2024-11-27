import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import bisect

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

    def __lt__(self, other):
        """Define how to compare two Task objects."""
        if not isinstance(other, Task):
            return NotImplemented
        return self.end_time < other.end_time  # Compare by end time (or use another field like start_time or priority)

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

# Merge Sort implementation
def merge_sort(tasks, key):
    """Sort the tasks using merge sort based on a given key."""
    if len(tasks) <= 1:
        return tasks
    
    # Divide the list in half
    mid = len(tasks) // 2
    left_half = merge_sort(tasks[:mid], key)
    right_half = merge_sort(tasks[mid:], key)
    
    # Merge the sorted halves
    return merge(left_half, right_half, key)

def merge(left, right, key):
    """Merge two sorted lists based on a given key."""
    sorted_list = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1
    
    # Append the remaining elements
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    
    return sorted_list

# Function to plot Gantt chart
def plot_gantt_chart(tasks):
    """Create and show a Gantt chart for tasks."""
    fig, ax = plt.subplots()  # Create figure
    for task in tasks:
        start = mdates.date2num(task.start_time)  # Convert start time to numeric format
        end = mdates.date2num(task.end_time)  # Convert end time to numeric format
        ax.barh(task.name, end - start, left=start, align='center', color='skyblue' if task.task_type == 'Personal' else 'orange')  # Color by task type
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Format time on x-axis
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Set hour intervals
    
    # Set limits using the correct method 'date2num' instead of 'dates2num'
    ax.set_xlim(mdates.date2num(min(task.start_time for task in tasks)),
                mdates.date2num(max(task.end_time for task in tasks)))  # Set limits
    
    plt.xlabel("Time")
    plt.ylabel("Tasks")
    plt.title("Task Schedule Gantt Chart")
    plt.show()  # Show the chart

# Function to check reminders
def check_for_reminders(tasks, current_time):
    """Check for approaching or missed task deadlines."""
    reminders = []  # List to hold reminders to be displayed in the GUI
    for task in tasks:
        time_to_deadline = task.deadline - current_time
        if timedelta(minutes=0) <= time_to_deadline <= timedelta(hours=1):
            reminders.append(f"Reminder: Task '{task.name}' deadline is approaching!")  # Upcoming deadline
        elif time_to_deadline < timedelta(minutes=0):
            reminders.append(f"Missed Deadline: Task '{task.name}' has missed its deadline!")  # Missed deadline
    return reminders

# Function to analyze busy time slots
def analyze_busy_slots(tasks, time_interval=30):
    """Analyze busy time slots based on task density within specified time intervals (in minutes)."""
    time_slots = {}  # Dictionary to store time slots and their task count
    for task in tasks:
        start = task.start_time
        end = task.end_time
        while start < end:
            # Round to nearest time interval (e.g., 30 minutes)
            rounded_time = start.replace(second=0, microsecond=0, minute=(start.minute // time_interval) * time_interval)
            time_slots[rounded_time] = time_slots.get(rounded_time, 0) + 1
            start += timedelta(minutes=time_interval)
    
    # Find the time slot with the maximum task density
    max_density_time = max(time_slots, key=time_slots.get)
    return max_density_time, time_slots[max_density_time]

# Searching functions
def search_task_by_name(tasks, task_name):
    """Search for a task by its name."""
    for task in tasks:
        if task.name.lower() == task_name.lower():
            return task  # Return the task if the name matches
    return None  # Return None if no task is found with the given name

def search_tasks_by_deadline(tasks, deadline_range_start, deadline_range_end):
    """Search for tasks within a specific deadline range."""
    result = []
    for task in tasks:
        if deadline_range_start <= task.deadline <= deadline_range_end:
            result.append(task)  # Add matching task to the result list
    return result  # Return list of tasks found within the deadline range

def search_tasks_by_priority(tasks, priority_level):
    """Search for tasks with a specific priority."""
    result = []
    for task in tasks:
        if task.priority == priority_level:
            result.append(task)  # Add task to list if it matches the priority
    return result  # Return list of tasks with the given priority

# Main application class
class TaskSchedulerApp:
    def __init__(self, root):
        """Setup the main window and task list."""
        self.root = root
        self.root.title("Task Scheduler")  # Set title
        self.root.geometry("600x600")  # Set size (increased to accommodate reminder area)
        self.root.configure(bg="#2c3e50")  # Set background color
        self.tasks = []  # Initialize task list

        self.reminder_label = None  # Label for reminders
        self.create_widgets()  # Create GUI components

    def create_widgets(self):
        """Create and organize all GUI elements."""
        self.create_header()  # Add header
        self.create_form_inputs()  # Add input fields for tasks
        self.create_buttons()  # Add action buttons
        self.create_footer()  # Add footer

        # Create reminder label to display upcoming and missed deadlines
        self.reminder_label = tk.Label(self.root, text="", font=("Helvetica", 12), fg="#e74c3c", bg="#2c3e50", justify="left")
        self.reminder_label.pack(pady=20, padx=20, fill='x')  # Add padding and set alignment

        # Periodic reminder check every 60 seconds
        self.root.after(60000, self.check_and_update_reminders)

        # Create search input and button
        self.create_search_widgets()

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

    def create_buttons(self):
        """Create action buttons for adding tasks, plotting, sorting, etc."""
        button_frame = tk.Frame(self.root, bg="#2c3e50")
        button_frame.pack(pady=10)  # Add padding around buttons

        # Buttons for adding task, showing tasks, plotting, etc.
        self.add_task_button = tk.Button(button_frame, text="Add Task", command=self.add_task, font=("Helvetica", 12), bg="#3498db", fg="#ecf0f1")
        self.add_task_button.grid(row=0, column=0, padx=10, pady=5)

        self.sort_button = tk.Button(button_frame, text="Sort Tasks by Priority", command=self.sort_tasks, font=("Helvetica", 12), bg="#2ecc71", fg="#ecf0f1")
        self.sort_button.grid(row=0, column=1, padx=10, pady=5)

        self.plot_button = tk.Button(button_frame, text="Plot Gantt Chart", command=self.plot_gantt_chart, font=("Helvetica", 12), bg="#9b59b6", fg="#ecf0f1")
        self.plot_button.grid(row=0, column=2, padx=10, pady=5)

    def create_footer(self):
        """Create footer for additional information or controls."""
        footer_label = tk.Label(
            self.root,
            text="© 2024 TaskSchedulerApp",
            font=("Helvetica", 8),
            fg="#bdc3c7",
            bg="#2c3e50"
        )
        footer_label.pack(side="bottom", pady=10)  # Add padding around footer

    def create_search_widgets(self):
        """Create search input field and button."""
        search_frame = tk.Frame(self.root, bg="#2c3e50")
        search_frame.pack(padx=20, pady=10, fill='x')  # Add padding around the frame

        # Search entry and button
        self.search_entry = tk.Entry(search_frame, font=("Helvetica", 12), bg="#ecf0f1")
        self.search_entry.grid(row=0, column=0, padx=10, pady=5, sticky='ew')

        self.search_button = tk.Button(search_frame, text="Search", font=("Helvetica", 12), bg="#f39c12", fg="#ecf0f1", command=self.on_search_button_click)
        self.search_button.grid(row=0, column=1, padx=10, pady=5)

    def add_task(self):
        """Callback for adding a new task."""
        try:
            # Get task details from input fields
            name = self.task_entries[0].get()
            task_type = self.task_type_var.get()
            priority = int(self.task_entries[2].get())
            start_time = datetime.strptime(self.task_entries[3].get(), "%H:%M")
            end_time = datetime.strptime(self.task_entries[4].get(), "%H:%M")
            deadline = datetime.strptime(self.task_entries[5].get(), "%Y-%m-%d %H:%M")

            # Create new Task object and add to the task list
            task = Task(name, task_type, priority, start_time, end_time, deadline)
            self.tasks.append(task)
            messagebox.showinfo("Success", "Task added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add task: {e}")

    def on_search_button_click(self):
        """Callback for search button click."""
        task_name = self.search_entry.get()  # Get the task name from the search input field
        task = search_task_by_name(self.tasks, task_name)
        if task:
            messagebox.showinfo("Task Found", f"Task found: {task}")  # Show the task details
        else:
            messagebox.showwarning("No Task Found", f"No task found with the name '{task_name}'")

    def check_and_update_reminders(self):
        """Check for reminders and update the UI."""
        current_time = datetime.now()  # Get the current time
        reminders = check_for_reminders(self.tasks, current_time)
        if reminders:
            self.reminder_label.config(text="\n".join(reminders))  # Update reminder label text
        else:
            self.reminder_label.config(text="")  # Clear reminder label if no reminders
        # Re-run the reminder check after 60 seconds
        self.root.after(60000, self.check_and_update_reminders)

    def sort_tasks(self):
        """Sort tasks based on priority and update the task list."""
        sorted_tasks = merge_sort(self.tasks, by="priority")  # Sort tasks by priority
        messagebox.showinfo("Sorted Tasks", "\n".join(str(task) for task in sorted_tasks))  # Show sorted tasks

    def plot_gantt_chart(self):
        """Plot and display a Gantt chart for the tasks."""
        plot_gantt_chart(self.tasks)

# Create the main application window
root = tk.Tk()
app = TaskSchedulerApp(root)

# Run the application
root.mainloop()
