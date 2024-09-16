import sys
import os
import multiprocessing
import psutil
from PIL import Image, ImageFilter
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QProgressBar
from PyQt5.QtCore import QTimer

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

class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Image Processing with Multi-core CPU")
        
        self.total_cores = multiprocessing.cpu_count()
        self.cpu_labels = []
        self.initUI()
        
        self.input_queue = multiprocessing.Queue()
        self.progress_queue = multiprocessing.Queue()
        
    def initUI(self):
        # Layout
        layout = QVBoxLayout()
        
        # CPU usage labels
        for i in range(self.total_cores):
            label = QLabel(f"Core {i+1}: 0%")
            layout.addWidget(label)
            self.cpu_labels.append(label)
        
        # Progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Processing...", self)
        layout.addWidget(self.status_label)
        
        # Start button
        start_button = QPushButton("Start Processing", self)
        start_button.clicked.connect(self.start_processing)
        layout.addWidget(start_button)
        
        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
    def update_cpu_usage(self):
        cpu_percentages = psutil.cpu_percent(percpu=True)
        for i, label in enumerate(self.cpu_labels):
            label.setText(f"Core {i+1}: {cpu_percentages[i]}%")
    
    def update_progress(self, total_images):
        processed_images = 0
        initial_progress = 5
        increment = (100 - initial_progress) / total_images
        
        while processed_images < total_images:
            self.progress_queue.get()  # Wait for a signal from the worker process
            processed_images += 1
            progress_value = initial_progress + processed_images * increment
            self.progress_bar.setValue(progress_value)
        
        # When processing is complete.
        self.progress_bar.setValue(100)
        self.status_label.setText("Complete")
    
    def start_processing(self):
        input_dir = 'input_images'
        output_dir = 'output_images'
        os.makedirs(output_dir, exist_ok=True)

        image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

        if not image_files:
            print("No images found in the input directory.")
            return

        for image_file in image_files:
            input_path = os.path.join(input_dir, image_file)
            output_path = os.path.join(output_dir, f"processed_{image_file}")
            self.input_queue.put((input_path, output_path))

        # Add sentinel values to indicate the end of the queue
        for _ in range(multiprocessing.cpu_count()):
            self.input_queue.put((None, None))

        processes = []
        for _ in range(multiprocessing.cpu_count()):
            process = multiprocessing.Process(target=process_image, args=(self.input_queue, self.progress_queue))
            processes.append(process)
            process.start()

        # Update progress in the main thread
        self.update_progress(len(image_files))

        for process in processes:
            process.join()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    
    # Timer for updating CPU usage every second
    timer = QTimer()
    timer.timeout.connect(window.update_cpu_usage)
    timer.start(1000)  # 1000 ms
    
    window.show()
    sys.exit(app.exec_())