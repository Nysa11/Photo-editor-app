from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PIL import Image, ImageEnhance, ImageFilter
import os

class ImageProcessor:
    def __init__(self):
        self.current_image = None
        self.current_filename = ''
        self.current_folder = ''  # To store the folder of the current image
        self.history = []  # To keep track of image states for undo

    def loadImage(self, folder, filename):
        self.current_folder = folder  # Save the folder where the image is located
        self.current_filename = filename
        image_path = os.path.join(folder, filename)
        self.current_image = Image.open(image_path)
        self.history = [self.current_image.copy()]  # Reset history with the original image

    def showImage(self, label):
        if self.current_image:
            self.current_image.save('temp.png')  # Save the current image as a temporary file
            pixmap = QPixmap('temp.png')  # Load the temporary file into QPixmap
            label.setPixmap(pixmap)  # Set the QPixmap on the QLabel

    def do_bw(self):
        if self.current_image:
            self.history.append(self.current_image.copy())  # Save current state to history
            self.current_image = self.current_image.convert("L")
            self.showImage(label_image)  # Refresh the displayed image

    def do_mirror(self):
        if self.current_image:
            self.history.append(self.current_image.copy())  # Save current state to history
            self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            self.showImage(label_image)  # Refresh the displayed image

    def do_blur(self):
        if self.current_image:
            self.history.append(self.current_image.copy())  # Save current state to history
            # Ensure image is in RGB mode before applying blur
            if self.current_image.mode != 'RGB':
                self.current_image = self.current_image.convert('RGB')
            self.current_image = self.current_image.filter(ImageFilter.GaussianBlur(5))  # Apply blur
            self.showImage(label_image)  # Refresh the displayed image


    def adjust_brightness_contrast(self, brightness_factor, contrast_factor):
        if self.current_image:
            self.history.append(self.current_image.copy())  # Save current state to history
            
            # Ensure image is in RGB mode before enhancing
            if self.current_image.mode != 'RGB':
                self.current_image = self.current_image.convert('RGB')
            
            enhancer_brightness = ImageEnhance.Brightness(self.current_image)
            enhancer_contrast = ImageEnhance.Contrast(self.current_image)
            self.current_image = enhancer_brightness.enhance(brightness_factor)
            self.current_image = enhancer_contrast.enhance(contrast_factor)
            
            self.showImage(label_image)  # Refresh the displayed image

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()  # Remove the last state
            self.current_image = self.history[-1].copy()  # Revert to the previous state
            self.showImage(label_image)  # Refresh the displayed image

    def saveImage(self):
        if self.current_image:
            # Create the "Modified" folder inside the current image's folder
            modified_dir = os.path.join(self.current_folder, 'Modified')
            os.makedirs(modified_dir, exist_ok=True)
            save_path = os.path.join(modified_dir, self.current_filename)
            self.current_image.save(save_path)
            print(f"Image saved to {save_path}")

app = QApplication([])
window = QWidget()
window.resize(700, 500)
window.setWindowTitle('Easy Editor')

# Interface elements
label_image = QLabel("Image")
label_image.setAlignment(Qt.AlignCenter)
list_files = QListWidget()

# Button elements
button_folder = QPushButton("Folder")
button_mirror = QPushButton("Mirror")
button_blur = QPushButton("Blur")  # New Blur Button
button_brightness_contrast = QPushButton("Brightness/Contrast")
button_bw = QPushButton("B/W")
button_undo = QPushButton("Undo")
button_save = QPushButton("Save")  # New Save Button

# Layout setup
row1 = QHBoxLayout()
row2 = QHBoxLayout()
column1 = QVBoxLayout()
column2 = QVBoxLayout()

column1.addWidget(button_folder)
column1.addWidget(list_files)

column2.addWidget(label_image)

row2.addWidget(button_mirror)
row2.addSpacing(10)
row2.addWidget(button_blur)  # Add Blur button
row2.addSpacing(10)
row2.addWidget(button_brightness_contrast)  # Add Brightness/Contrast button
row2.addSpacing(10)
row2.addWidget(button_bw)
row2.addSpacing(10)
row2.addWidget(button_undo)
row2.addSpacing(10)
row2.addWidget(button_save)  # Add Save button

column2.addLayout(row2)

row1.addLayout(column1)
row1.addLayout(column2)

window.setLayout(row1)

# Global variable to store the selected work directory
workdir = ''

# Event handling function to open folder dialog and set workdir
def chooseWorkdir():
    global workdir
    workdir = QFileDialog.getExistingDirectory(window, 'Select Folder', os.getcwd())
    if workdir:
        handler()

# Function to filter and return files with specific extensions
def filter():
    extensions = ['.png', '.jpg', '.jpeg', '.gif']
    return [file_name for file_name in os.listdir(workdir) if any(file_name.lower().endswith(ext) for ext in extensions)]

# Handler function for Folder button click
def handler():
    if workdir:
        list_files.clear()
        filtered_files = filter()
        for file_name in filtered_files:
            item = QListWidgetItem(file_name)
            item.setForeground(QColor('white'))  # Set file name color to white
            list_files.addItem(item)

# Create an instance of ImageProcessor
image_processor = ImageProcessor()

# Event handling for selecting a file from the list
def onFileSelected(item):
    filename = item.text()
    image_processor.loadImage(workdir, filename)
    image_processor.showImage(label_image)

# Function to apply filters
def apply_bw():
    image_processor.do_bw()

def apply_mirror():
    image_processor.do_mirror()

def apply_blur():
    image_processor.do_blur()  # Apply blur effect

def apply_brightness_contrast():
    image_processor.adjust_brightness_contrast(1.5, 1.2)  # Example adjustment

# Connect signals and slots
button_folder.clicked.connect(chooseWorkdir)
list_files.itemClicked.connect(onFileSelected)
button_bw.clicked.connect(apply_bw)
button_mirror.clicked.connect(apply_mirror)
button_blur.clicked.connect(apply_blur)  # Connect Blur button to apply_blur function
button_brightness_contrast.clicked.connect(apply_brightness_contrast)
button_undo.clicked.connect(image_processor.undo)
button_save.clicked.connect(image_processor.saveImage)  # Connect Save button to saveImage method

# Set background color of window and other styles
window.setStyleSheet("""
    QWidget {
        background-color: #222222;
        color: white;
    }
    QPushButton {
        background-color: #444444;
        color: white;
        border: none;
        padding: 10px;
    }
    QPushButton:hover {
        background-color: #555555;
    }
    QPushButton:pressed {
        background-color: #ffffff;
        color: #222222;
    }
    QLabel {
        color: white;
    }
    QListWidget {
        background-color: #333333;
        color: white;
    }
""")

# Show the main window
window.show()

# Start the application event loop
app.exec_()
