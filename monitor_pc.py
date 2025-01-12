import psutil
import tkinter as tk
from tkinter import ttk
import platform
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import GPUtil

# Initialize global variables
is_monitoring = True
update_interval = 1000  # Default 1-second update interval
theme = "dark"

# Function to toggle monitoring
def toggle_monitoring():
    global is_monitoring
    is_monitoring = not is_monitoring
    if is_monitoring:
        toggle_button.config(text="Pause Monitoring")
        update_stats()
    else:
        toggle_button.config(text="Start Monitoring")

# Function to update system stats
def update_stats():
    if not is_monitoring:
        return

    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')
    net_info = psutil.net_io_counters()
    gpu_info = get_gpu_info()

    # Update Labels
    cpu_label.config(text=f"CPU Usage: {cpu_percent}%", foreground=color_by_usage(cpu_percent))
    memory_label.config(text=f"Memory Usage: {memory_info.percent}% ({memory_info.used // (1024**2)} MB / {memory_info.total // (1024**2)} MB)", foreground=color_by_usage(memory_info.percent))
    disk_label.config(text=f"Disk Usage: {disk_info.percent}% ({disk_info.used // (1024**3)} GB / {disk_info.total // (1024**3)} GB)", foreground=color_by_usage(disk_info.percent))
    net_label.config(text=f"Network Sent: {net_info.bytes_sent // (1024**2)} MB | Received: {net_info.bytes_recv // (1024**2)} MB")
    gpu_label.config(text="\n".join(
        [f"GPU: {gpu['name']}, Load: {gpu['load']}, Mem: {gpu['memory_used']}/{gpu['memory_total']}, Temp: {gpu['temperature']}"
         for gpu in gpu_info]
    ), foreground=color_by_usage(float(gpu_info[0]['load'].split()[0][:-1])))

    # Update Progress Bars
    cpu_progress['value'] = cpu_percent
    memory_progress['value'] = memory_info.percent
    disk_progress['value'] = disk_info.percent
    gpu_progress['value'] = float(gpu_info[0]['memory_used'].split()[0]) / float(gpu_info[0]['memory_total'].split()[0]) * 100
  
    # Update Graph Data
    x_values.append(datetime.datetime.now().strftime('%H:%M:%S'))
    cpu_data.append(cpu_percent)
    if len(x_values) > 20:  # Keep graph size manageable
        x_values.pop(0)
        cpu_data.pop(0)

    # Update Graph
    ax.clear()
    ax.plot(x_values, cpu_data, color="cyan", linewidth=2)
    ax.set_title("CPU Usage Over Time", fontsize=10, color="white" if theme == "dark" else "black")
    ax.set_facecolor("#333333" if theme == "dark" else "#F0F0F0")
    ax.tick_params(axis='x', labelsize=8, colors="white" if theme == "dark" else "black")
    ax.tick_params(axis='y', labelsize=8, colors="white" if theme == "dark" else "black")
    ax.spines['bottom'].set_color("white" if theme == "dark" else "black")
    ax.spines['left'].set_color("white" if theme == "dark" else "black")
    ax.spines['top'].set_color("white" if theme == "dark" else "black")
    ax.spines['right'].set_color("white" if theme == "dark" else "black")
    fig_canvas.draw()

    root.after(update_interval, update_stats)

def get_gpu_info():
    """Retrieve GPU details."""
    gpus = GPUtil.getGPUs()
    gpu_info = []
    for gpu in gpus:
        gpu_info.append({
            "name": gpu.name,
            "load": f"{gpu.load * 100:.2f}%",
            "memory_free": f"{gpu.memoryFree} MB",
            "memory_used": f"{gpu.memoryUsed} MB",
            "memory_total": f"{gpu.memoryTotal} MB",
            "temperature": f"{gpu.temperature} °C",
        })
    return gpu_info


def update_gpu_info():
    gpu_info = get_gpu_info()
    gpu_label.config(text="\n".join(
        [f"GPU: {gpu['name']}, Load: {gpu['load']}, Mem: {gpu['memory_used']}/{gpu['memory_total']}, Temp: {gpu['temperature']}"
         for gpu in gpu_info]
    ))
    
    root.after(2000, update_gpu_info)  # Refresh every 2 seconds

# Function to determine color by usage percentage
def color_by_usage(usage):
    if usage < 50:
        return "green"
    elif usage < 75:
        return "orange"
    else:
        return "red"

# Function to toggle theme
def toggle_theme():
    global theme
    theme = "light" if theme == "dark" else "dark"
    root.configure(bg="#1E1E1E" if theme == "dark" else "#FFFFFF")
    title_label.config(bg="#1E1E1E" if theme == "dark" else "#FFFFFF", fg="white" if theme == "dark" else "black")
    system_label.config(bg="#1E1E1E" if theme == "dark" else "#FFFFFF", fg="white" if theme == "dark" else "black")
    processor_label.config(bg="#1E1E1E" if theme == "dark" else "#FFFFFF", fg="white" if theme == "dark" else "black")
    net_label.config(bg="#1E1E1E" if theme == "dark" else "#FFFFFF", fg="white" if theme == "dark" else "black")
    date_time_label.config(bg="#1E1E1E" if theme == "dark" else "#FFFFFF", fg="white" if theme == "dark" else "black")
    gpu_label.config(bg="#1E1E1E" if theme == "dark" else "#FFFFFF", fg="white" if theme == "dark" else "black")

# Function to update the update interval
def set_update_interval(*args):
    global update_interval
    selected_value = interval_var.get()
    update_interval = int(selected_value) * 1000

# Create the GUI application
root = tk.Tk()
root.title("Interactive PC Monitor")
root.geometry("1000x1000")
root.configure(bg="#1E1E1E")
root.iconphoto(True, tk.PhotoImage(file="/home/stefanos/Desktop/specs.png"))  # Update with the path to your icon

# Title
title_label = tk.Label(root, text="Interactive PC Monitor", font=("Helvetica", 20, "bold"), bg="#1E1E1E", fg="white")
title_label.pack(pady=10)

# System Info
system_info = platform.uname()
system_label = tk.Label(root, text=f"System: {system_info.system} {system_info.release}", font=("Helvetica", 12), bg="#1E1E1E", fg="white")
system_label.pack()
processor_label = tk.Label(root, text=f"Processor: {system_info.processor}", font=("Helvetica", 12), bg="#1E1E1E", fg="white")
processor_label.pack()

# CPU Usage
cpu_label = tk.Label(root, text="CPU Usage: ", font=("Helvetica", 12), bg="#1E1E1E", fg="white")
cpu_label.pack(pady=5)
cpu_progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", maximum=100)
cpu_progress.pack(pady=5)

# Memory Usage
memory_label = tk.Label(root, text="Memory Usage: ", font=("Helvetica", 12), bg="#1E1E1E", fg="white")
memory_label.pack(pady=5)
memory_progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", maximum=100)
memory_progress.pack(pady=5)

# Disk Usage
disk_label = tk.Label(root, text="Disk Usage: ", font=("Helvetica", 12), bg="#1E1E1E", fg="white")
disk_label.pack(pady=5)
disk_progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", maximum=100)
disk_progress.pack(pady=5)

# Network Usage
net_label = tk.Label(root, text="Network Sent: 0 MB | Received: 0 MB", font=("Helvetica", 12), bg="#1E1E1E", fg="white")
net_label.pack(pady=10)

# GPU label 
gpu_label = tk.Label(root, text="Loading GPU info...", font=("Helvetica", 12), bg="#1E1E1E", fg="white")
gpu_label.pack()
gpu_progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", maximum=100)
gpu_progress.pack(pady=5)

# Current Date and Time
date_time_label = tk.Label(root, text=f"Date & Time: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}", font=("Helvetica", 12), bg="#1E1E1E", fg="white")
date_time_label.pack(pady=5)

# Buttons
toggle_button = tk.Button(root, text="Pause Monitoring", command=toggle_monitoring, bg="gray", fg="white")
toggle_button.pack(pady=5)

theme_button = tk.Button(root, text="Toggle Theme", command=toggle_theme, bg="gray", fg="white")
theme_button.pack(pady=5)

exit_button = tk.Button(root, text="Exit", command=root.quit, bg="red", fg="white")
exit_button.pack(pady=5)

# Dropdown for Update Interval
interval_var = tk.StringVar(value="1")
interval_dropdown = ttk.Combobox(root, textvariable=interval_var, values=["1", "2", "5", "10"])
interval_dropdown.pack(pady=10)
interval_dropdown.bind("<<ComboboxSelected>>", set_update_interval)
interval_label = tk.Label(root, text="Select Update Interval (seconds):", font=("Helvetica", 10), bg="#1E1E1E", fg="white")
interval_label.pack()

# Graph for CPU Usage
x_values = []
cpu_data = []

fig, ax = plt.subplots(figsize=(5, 2), dpi=100)
fig.patch.set_facecolor('#1E1E1E')
fig_canvas = FigureCanvasTkAgg(fig, master=root)
fig_canvas.get_tk_widget().pack()

# Update time and stats
update_stats()
update_gpu_info()

# Run the application
root.mainloop()
