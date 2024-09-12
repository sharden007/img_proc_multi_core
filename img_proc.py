import multiprocessing
import psutil
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageFilter

# Function to process an image by applying a filter.
def process_image(input_queue, progress_queue):
    while True:
        image_path, output_path = input_queue.get()
        if image_path is None:
            break
        try:
            with Image.open(image_path) as img:
                filtered_img = img.filter(ImageFilter.GaussianBlur(5))
                filtered_img.save(output_path)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
        finally:
            progress_queue.put(1)  # Signal that one image has been processed

# Function to update CPU usage per core
def update_cpu_usage(cpu_labels):
    cpu_percentages = psutil.cpu_percent(percpu=True)
    for i, label in enumerate(cpu_labels):
        label.config(text=f"Core {i+1}: {cpu_percentages[i]}%")
    root.after(1000, update_cpu_usage, cpu_labels)  # Update every second

def update_progress(progress_var, progress_queue, total_images, status_label):
    processed_images = 0
    initial_progress = 5
    progress_var.set(initial_progress)  # Start at 5%
    increment = (100 - initial_progress) / total_images  # Calculate increment per image

    while processed_images < total_images:
        progress_queue.get()  # Wait for a signal from the worker process
        processed_images += 1
        progress_var.set(initial_progress + processed_images * increment)
        root.update_idletasks()  # Update the GUI

    # When processing is complete.
    progress_var.set(100)
    status_label.config(text="Complete", foreground="green")

def start_processing():
    input_dir = 'input_images'
    output_dir = 'output_images'
    os.makedirs(output_dir, exist_ok=True)

    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        messagebox.showwarning("No Images", "No images found in the input directory.")
        return

    input_queue = multiprocessing.Queue()
    progress_queue = multiprocessing.Queue()

    for image_file in image_files:
        input_path = os.path.join(input_dir, image_file)
        output_path = os.path.join(output_dir, f"processed_{image_file}")
        input_queue.put((input_path, output_path))

    # Add sentinel values to indicate the end of the queue
    for _ in range(multiprocessing.cpu_count()):
        input_queue.put((None, None))

    processes = []
    for _ in range(multiprocessing.cpu_count()):
        process = multiprocessing.Process(target=process_image, args=(input_queue, progress_queue))
        processes.append(process)
        process.start()

    # Update progress in the main thread
    update_progress(progress_var, progress_queue, len(image_files), status_label)

    for process in processes:
        process.join()

if __name__ == '__main__':
    # Set up the GUI
    root = tk.Tk()
    root.title("Image Processing with Multi-core CPU")

    total_cores = multiprocessing.cpu_count()

    # Create labels for each CPU core
    cpu_labels = []
    for i in range(total_cores):
        label = tk.Label(root, text=f"Core {i+1}: 0%")
        label.pack(pady=2)
        cpu_labels.append(label)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, padx=20, pady=10)

    # Status label
    status_label = tk.Label(root, text="Processing...", foreground="black")
    status_label.pack(pady=5)

    start_button = tk.Button(root, text="Start Processing", command=start_processing)
    start_button.pack(pady=10)

    update_cpu_usage(cpu_labels)

    root.mainloop()