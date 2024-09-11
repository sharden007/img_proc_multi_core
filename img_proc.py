import multiprocessing
import psutil
import time
from PIL import Image, ImageFilter
import os

# Function to process an image by applying a filter
def process_image(image_path, output_path):
    try:
        # Open an image file
        with Image.open(image_path) as img:
            # Apply a filter to the image
            filtered_img = img.filter(ImageFilter.GaussianBlur(5))
            # Save the processed image to the output path
            filtered_img.save(output_path)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

# Function to display CPU usage per core
def display_cpu_usage():
    while True:
        # Get CPU usage for each core
        cpu_percentages = psutil.cpu_percent(percpu=True)
        # Print CPU usage
        print(f"CPU Usage per core: {cpu_percentages}")
        time.sleep(1)  # Update every second

if __name__ == '__main__':
    # Directory containing images to process
    input_dir = 'input_images'
    # Directory to save processed images
    output_dir = 'output_images'
    os.makedirs(output_dir, exist_ok=True)

    # List all image files in the input directory
    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # Create a process for monitoring CPU usage
    monitor_process = multiprocessing.Process(target=display_cpu_usage)
    monitor_process.start()

    # Create and start image processing processes
    processes = []
    for image_file in image_files:
        input_path = os.path.join(input_dir, image_file)
        output_path = os.path.join(output_dir, f"processed_{image_file}")
        process = multiprocessing.Process(target=process_image, args=(input_path, output_path))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()

    # Terminate the monitoring process
    monitor_process.terminate()