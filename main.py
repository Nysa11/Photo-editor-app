from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor
from PIL import Image, ImageEnhance, ImageFilter
import os


class ImageProcessor:
    def __init__(self):
        self.current_image = None
        self.current_filename = ''
        self.current_folder = ''  # To store the folder of the current image
        self.history = []  # To keep track of image states for undo

    def load_image(self, folder, filename):
        self.current_folder = folder  # Save the folder where the image is located
        self.current_filename = filename
        image_path = os.path.join(folder, filename)
        self.current_image = Image.open(image_path)
        self.history = [self.current_image.copy()]  # Reset history with the original image

    def show_image(self, label):
        if self.current_image:
            self.current_image.save('temp.png')  # Save the current image as a temporary file
            pixmap = QPixmap('temp.png')  # Load the temporary file into QPixmap
            label.setPixmap(pixmap)  # Set the QPixmap on the QLabel

    def do_bw(self, label):
        if self.current_image:
            self.history.append(self.current_image.copy())  # Save current state to history
            self.current_image = self.current_image.convert("L")
            self.show_image(label)  # Refresh the displayed image

    def do_mirror(self, label):
        if self.current_image:
            self.history.append(self.current_image.copy())  # Save current state to history
            self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            self.show_image(label)  # Refresh the displayed image

    def do_blur(self, label):
        if self.current_image:
            self.history.append(self.current_image.copy())  # Save current state to history
            # Ensure image is in RGB mode before applying blur
            if self.current_image.mode != 'RGB':
                self.current_image = self.current_image.convert('RGB')
            self.current_image = self.current_image.filter(ImageFilter.GaussianBlur(5))  # Apply blur
            self.show_image(label)  # Refresh the displayed image

    def adjust_brightness_contrast(self, label, brightness_factor, contrast_factor):
        if self.current_image:
            self.history.append(self.current_image.copy())  # Save current state to history

            # Ensure image is in RGB mode before enhancing
            if self.current_image.mode != 'RGB':
                self.current_image = self.current_image.convert('RGB')
            enhancer_brightness = ImageEnhance.Brightness(self.current_image)
            enhancer_contrast = ImageEnhance.Contrast(self.current_image)
            self.current_image = enhancer_brightness.enhance(brightness_factor)
            self.current_image = enhancer_contrast.enhance(contrast_factor)
            self.show_image(label)  # Refresh the displayed image

    def undo(self, label):
        if len(self.history) > 1:
            self.history.pop()  # Remove the last state
            self.current_image = self.history[-1].copy()  # Revert to the previous state
            self.show_image(label)  # Refresh the displayed image

    def save_image(self):
        if self.current_image:
            # Create the "Modified" folder inside the current image's folder
            modified_dir = os.path.join(self.current_folder, 'Modified')
            os.makedirs(modified_dir, exist_ok=True)
            save_path = os.path.join(modified_dir, self.current_filename)
            self.current_image.save(save_path)
            print(f"Image saved to {save_path}")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Editor")
        self.resize(800, 600)
        
        self.image_processor = ImageProcessor()
        self.is_light_mode = True
        self.opacity = 1.0

        self.setup_ui()
        self.setup_styles()
        self.setup_connections()

    def setup_ui(self):
        # Interface elements
        self.label_image = QLabel("Image")
        self.label_image.setAlignment(Qt.AlignCenter)
        
        self.button_select_folder = QPushButton("Select Folder")
        self.button_toggle_mode = QPushButton("Switch to Dark Mode") # New Mode Button
        self.button_mirror = QPushButton("Mirror")
        self.button_blur = QPushButton("Blur")
        self.button_brightness_contrast = QPushButton("Brightness/Contrast")
        self.button_bw = QPushButton("B/W")
        self.button_undo = QPushButton("Undo")
        self.button_save = QPushButton("Save")

        self.list_files = QListWidget()

        # Layout setup
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_select_folder)
        layout_buttons.addWidget(self.button_toggle_mode)

        layout_image = QVBoxLayout()
        layout_image.addWidget(self.label_image)

        layout_processing_buttons = QHBoxLayout()
        layout_processing_buttons.addWidget(self.button_mirror)
        layout_processing_buttons.addWidget(self.button_blur)
        layout_processing_buttons.addWidget(self.button_brightness_contrast)
        layout_processing_buttons.addWidget(self.button_bw)
        layout_processing_buttons.addWidget(self.button_undo)
        layout_processing_buttons.addWidget(self.button_save)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_image)
        main_layout.addLayout(layout_buttons)
        main_layout.addLayout(layout_processing_buttons)
        main_layout.addWidget(self.list_files)

        self.setLayout(main_layout)

    def setup_styles(self):
        # Different modes
        self.light_mode_stylesheet = """
            QWidget { background-color: #f5f5f5; color: black; }
            QPushButton { background-color: #ddd; color: black; border-radius: 5px; }
            QListWidget { background-color: #fff; color: black; }
        """
        self.dark_mode_stylesheet = """
            QWidget { background-color: #222; color: white; }
            QPushButton { background-color: #444; color: white; border-radius: 5px; }
            QListWidget { background-color: #333; color: white; }
        """
        self.setStyleSheet(self.light_mode_stylesheet)

    def setup_connections(self):
        self.button_select_folder.clicked.connect(self.chooseWorkdir) 
        self.button_toggle_mode.clicked.connect(self.start_mode_transition)
        self.list_files.itemClicked.connect(self.onFileSelected)
        self.button_bw.clicked.connect(lambda: self.image_processor.do_bw(self.label_image))
        self.button_mirror.clicked.connect(lambda: self.image_processor.do_mirror(self.label_image))
        self.button_blur.clicked.connect(lambda: self.image_processor.do_blur(self.label_image))
        self.button_brightness_contrast.clicked.connect(lambda: self.image_processor.adjust_brightness_contrast(self.label_image, 1.5, 1.2))
        self.button_undo.clicked.connect(lambda: self.image_processor.undo(self.label_image))
        self.button_save.clicked.connect(self.image_processor.save_image)

    def start_mode_transition(self):
        self.fade_out()

    def fade_out(self):
        self.opacity = 1.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.reduce_opacity)
        self.timer.start(50)

    def reduce_opacity(self):
        if self.opacity > 0:
            self.opacity -= 0.1
            self.setWindowOpacity(self.opacity)
        else:
            self.timer.stop()
            self.toggle_mode()
            self.fade_in()

    def toggle_mode(self):
        if self.is_light_mode:
            self.setStyleSheet(self.dark_mode_stylesheet)
            self.button_toggle_mode.setText("Switch to Light Mode")
        else:
            self.setStyleSheet(self.light_mode_stylesheet)
            self.button_toggle_mode.setText("Switch to Dark Mode")
        self.is_light_mode = not self.is_light_mode
        self.update_file_list_colors()

    def fade_in(self):
        self.opacity = 0.0
        self.setWindowOpacity(self.opacity)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.increase_opacity)
        self.timer.start(50)

    def increase_opacity(self):
        if self.opacity < 1.0:
            self.opacity += 0.1
            self.setWindowOpacity(self.opacity)
        else:
            self.timer.stop()

    # Event handling function to open folder dialog and set workdir
    def chooseWorkdir(self):
        # Global variable to store the selected work directory
        global workdir
        workdir = QFileDialog.getExistingDirectory(self, 'Select Folder', os.getcwd())
        if workdir:
            self.handler()

    def load_files(self, workdir):
        self.list_files.clear()
        filtered_files = self.filter_files(workdir)
        for file_name in filtered_files:
            item = QListWidgetItem(file_name)
            item.setForeground(QColor('black' if self.is_light_mode else 'white'))
            self.list_files.addItem(item)

    # Handler function for Folder button click
    def handler(self):
        if self:
            self.list_files.clear()
            filtered_files = self.filter_files(workdir)
            for file_name in filtered_files:
                item = QListWidgetItem(file_name)
                item.setForeground(QColor('black' if self.is_light_mode else 'white'))   # Set file name color to white if dark mode and black if light mode
                self.list_files.addItem(item)

    # Function to filter and return files with specific extensions
    def filter_files(self, folder):
        extensions = ['.png', '.jpg', '.jpeg', '.gif']
        return [file_name for file_name in os.listdir(folder) if any(file_name.lower().endswith(ext) for ext in extensions)]

    # Event handling for selecting a file from the list
    def onFileSelected(self, item):
        filename = item.text()
        self.image_processor.load_image(workdir, filename)
        self.image_processor.show_image(self.label_image)

    def update_file_list_colors(self):
        for index in range(self.list_files.count()):
            item = self.list_files.item(index)
            item.setForeground(QColor('black' if self.is_light_mode else 'white'))

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()