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

# Sorting function for tasks
def sort_tasks(tasks, by="priority"):
    """Sort tasks by priority, start time, end time, or task type."""
    if by == "priority":
        tasks.sort(key=lambda x: x.priority, reverse=True)  # Sort by priority (high to low)
    elif by == "start_time":
        tasks.sort(key=lambda x: x.start_time)  # Sort by start time
    elif by == "end_time":
        tasks.sort(key=lambda x: x.end_time)  # Sort by end time
    elif by == "task_type":
        tasks.sort(key=lambda x: x.task_type)  # Sort by task type
    return tasks

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
            sort_by = "priority"  # Or use any other sorting criteria
            sorted_tasks = sort_tasks(self.tasks, by=sort_by)  # Sort tasks by the chosen criteria
            plot_gantt_chart(sorted_tasks)  # Show Gantt chart
        else:
            messagebox.showinfo("No Tasks", "You need to add tasks to view the Gantt chart.")  # No tasks message

    def check_and_update_reminders(self):
        """Check and update reminders every minute."""
        current_time = datetime.now()  # Get current time
        reminders = check_for_reminders(self.tasks, current_time)  # Get reminders
        if reminders:
            self.reminder_label.config(text="\n".join(reminders))  # Update reminder label with reminders
        else:
            self.reminder_label.config(text="No upcoming or missed deadlines.")  # Reset if no reminders
        self.root.after(60000, self.check_and_update_reminders)  # Re-check after 60 seconds

# Main execution
if __name__ == "__main__":
    root = tk.Tk()  # Create the main window
    app = TaskSchedulerApp(root)  # Start the application
    root.mainloop()  # Run the GUI event loop
"""

Example Tasks for Gantt Chart
Task 1

Name: "Task A"
Type: "Personal"
Priority: 3
Start Time: 09:00
End Time: 11:00
Deadline: 2024-11-23 12:00
Task A

Name: "Task B"
Type: "Academic"
Priority: 5
Start Time: 10:30
End Time: 13:00
Deadline: 2024-11-23 15:00
Task B

Name: "Task C"
Type: "Personal"
Priority: 2
Start Time: 13:00
End Time: 15:30
Deadline: 2024-11-23 16:00
Task C

Name: "Task D"
Type: "Academic"
Priority: 4
Start Time: 14:30
End Time: 17:00
Deadline: 2024-11-23 18:00
Task D

Name: "Task A"
Type: "Personal"
Priority: 1
Start Time: 16:00
End Time: 18:00
Deadline: 2024-11-23 19:00
How to Input These Tasks into the GUI
Add Task A (Task A):

Task Name: "Task B"
Task Type: "Personal"
Priority: 3
Start Time: 09:00
End Time: 11:00
Deadline: 2024-11-23 12:00
Add Task B (Task B):

Task Name: "Task B"
Task Type: "Academic"
Priority: 5
Start Time: 10:30
End Time: 13:00
Deadline: 2024-11-23 15:00
Add Task 3 (Task C):

Task Name: "Task C"
Task Type: "Personal"
Priority: 2
Start Time: 13:00
End Time: 15:30
Deadline: 2024-11-23 16:00
Add Task 4 (Task D):

Task Name: "Task D"
Task Type: "Academic"
Priority: 4
Start Time: 14:30
End Time: 17:00
Deadline: 2024-11-23 18:00
Add Task 5 (Task E):

Task Name: "Task E"
Task Type: "Personal"
Priority: 1
Start Time: 16:00
End Time: 18:00
Deadline: 2024-11-23 19:00
What Happens in the Gantt Chart:
When you View Gantt Chart after adding the tasks, the chart will display a horizontal bar for each task, aligned with their respective start and end times.
Task A will be shown from 09:00 to 11:00.
Task B will be shown from 10:30 to 13:00.
Task C will be shown from 13:00 to 15:30.
Task D will be shown from 14:30 to 17:00.
Task E will be shown from 16:00 to 18:00.
Visualization of the Gantt Chart:
The Gantt chart will be a horizontal bar chart, with the Y-axis showing the task names (e.g., Task A, Task B, Task C, etc.), and the X-axis showing the time (with hours marked on the X-axis). Each task will be represented by a horizontal bar where:

The left side of the bar represents the start time of the task.
The right side of the bar represents the end time of the task.
The bar length will represent the duration of the task.
For example:

"Task A" will have a bar starting at 09:00 and ending at 11:00.
"Task B" will have a bar starting at 10:30 and ending at 13:00, partially overlapping with "Task A".
"Task C" will have a bar starting at 13:00 and ending at 15:30, overlapping with both "Task B" and "Task D".
"Task D" will have a bar starting at 14:30 and ending at 17:00, overlapping with "Task C" and "Task E".
"Task E" will have a bar starting at 16:00 and ending at 18:00, overlapping with "Task D".""" 
