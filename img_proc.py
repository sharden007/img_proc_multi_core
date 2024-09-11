import multiprocessing
import psutil
import time
from PIL import Image, ImageFilter
import os
import tkinter as tk
from tkinter import ttk

# Function to process an image by applying a filter
def process_image(image_path, output_path, progress_var, progress_step):
    try:
        # Open an image file
        with Image.open(image_path) as img:
            # Apply a filter to the image
            filtered_img = img.filter(ImageFilter.GaussianBlur(5))
            # Save the processed image to the output path
            filtered_img.save(output_path)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    finally:
        # Update progress bar
        progress_var.set(progress_var.get() + progress_step)

# Function to display CPU usage per core
def update_cpu_usage(cpu_label):
    cpu_percentages = psutil.cpu_percent(percpu=True)
    cpu_label.config(text=f"CPU Usage per core: {cpu_percentages}")
    cpu_label.after(1000, update_cpu_usage, cpu_label)  # Update every second

def start_processing():
    # Directory containing images to process
    input_dir = 'input_images'
    # Directory to save processed images
    output_dir = 'output_images'
    os.makedirs(output_dir, exist_ok=True)

    # List all image files in the input directory
    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # Create and start image processing processes
    processes = []
    progress_step = 100 / len(image_files)  # Calculate step for progress bar
    for image_file in image_files:
        input_path = os.path.join(input_dir, image_file)
        output_path = os.path.join(output_dir, f"processed_{image_file}")
        process = multiprocessing.Process(target=process_image, args=(input_path, output_path, progress_var, progress_step))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()

# Set up the GUI
root = tk.Tk()
root.title("Image Processing with Multi-core CPU")

# CPU Usage Label
cpu_label = tk.Label(root, text="CPU Usage per core: ")
cpu_label.pack(pady=10)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=20, pady=10)

# Start Button
start_button = tk.Button(root, text="Start Processing", command=start_processing)
start_button.pack(pady=10)

# Start updating CPU usage
update_cpu_usage(cpu_label)

# Start the GUI event loop
root.mainloop()