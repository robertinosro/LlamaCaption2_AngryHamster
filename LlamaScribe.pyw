import os
import shutil
import base64
import requests
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar, QFileDialog, QWidget, QTabWidget, QTextEdit, QLineEdit, QGridLayout, QComboBox, QCheckBox, QGroupBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Set up logging
logging.basicConfig(filename='llamascribe_debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')  # 'w' mode overwrites the file each time

# Constants
IMAGES_FOLDER = "Processed_images_with_captions"
SYSTEM_PROMPT_LLAVA = "describe what the image shows"
DEFAULT_PROMPT_TEMPLATE = ("you are a captioning expert, you will be given an image description and you should describe "
                            "what is shown in the image as if you were describing the image to a blind person. "
                            "your response should only be the description of the image and nothing else. "
                            "Do not include explanations of the description or add any further details. "
                            "IMPORTANT: Your response must be in a single line with no line breaks.")

# Default prefix and suffix - users can modify these in the source code
DEFAULT_CAPTION_PREFIX = "A photo of a woman, bloobikkx1, curvy blonde with (a well-defined neck:1.3) and (natural proportions:1.2), "
DEFAULT_CAPTION_SUFFIX = " (masterpiece, ultra-realistic, high-definition, 8K, cinematic lighting),(professional photography:1.4), (sharp focus:1.2), (studio lighting:1.2), (clear details:1.3), (professional atmosphere:1.3)"

def load_api_endpoint(config_file="config.txt"):
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            for line in f:
                if line.startswith("API_ENDPOINT="):
                    return line.split("=", 1)[1].strip()
    return "http://localhost:11434"  # Default fallback endpoint

API_ENDPOINT = load_api_endpoint()

def fetch_installed_models():
        try:
            response = requests.get(f"{API_ENDPOINT}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            else:
                print(f"Error fetching models: {response.text}")
                return []
        except Exception as e:
            print(f"Exception while fetching models: {e}")
            return []

# Worker Thread for processing
class CaptioningWorker(QThread):
    progress = pyqtSignal(str, int)  # Emit current task and progress percentage
    finished = pyqtSignal()

    def __init__(self, source_folder, prompt_template, llava_model, qwen_model, 
                 use_prefix, custom_prefix, use_suffix, custom_suffix):
        super().__init__()
        self.source_folder = source_folder
        self.prompt_template = prompt_template
        self.llava_model = llava_model
        self.qwen_model = qwen_model
        self.use_prefix = use_prefix
        self.custom_prefix = custom_prefix if custom_prefix else DEFAULT_CAPTION_PREFIX
        self.use_suffix = use_suffix
        self.custom_suffix = custom_suffix if custom_suffix else DEFAULT_CAPTION_SUFFIX

    def run(self):
        self.progress.emit("Selecting and copying images", 10)
        self.prepare_images()
        self.progress.emit("Converting images to PNG", 30)
        self.convert_to_png()
        self.progress.emit("Captioning images with custom format", 60)
        self.caption_images()
        self.progress.emit("Process complete", 100)
        self.finished.emit()

    def prepare_images(self):
        if not self.source_folder:
            raise FileNotFoundError("No folder was selected.")

        if not os.path.exists(self.source_folder):
            raise FileNotFoundError(f"Source folder {self.source_folder} does not exist.")

        if os.path.exists(IMAGES_FOLDER):
            shutil.rmtree(IMAGES_FOLDER)
        os.makedirs(IMAGES_FOLDER, exist_ok=True)

        for file_name in os.listdir(self.source_folder):
            source_path = os.path.join(self.source_folder, file_name)
            if os.path.isfile(source_path):
                shutil.copy2(source_path, IMAGES_FOLDER)

    def convert_to_png(self):
        for file_name in os.listdir(IMAGES_FOLDER):
            source_path = os.path.join(IMAGES_FOLDER, file_name)
            file_stem, file_ext = os.path.splitext(file_name)
            if file_ext.lower() != ".png":
                new_path = os.path.join(IMAGES_FOLDER, f"{file_stem}.png")
                try:
                    from PIL import Image
                    with Image.open(source_path) as img:
                        img.save(new_path, "PNG")
                    os.remove(source_path)
                except Exception as e:
                    print(f"Error converting {file_name}: {e}")

    def caption_images(self):
        for file_name in os.listdir(IMAGES_FOLDER):
            if not file_name.endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            image_path = os.path.join(IMAGES_FOLDER, file_name)
            logging.debug(f"Processing image: {image_path}")
            
            try:
                with open(image_path, "rb") as img_file:
                    encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

                payload = {
                    "model": self.llava_model,
                    "prompt": SYSTEM_PROMPT_LLAVA,
                    "images": [encoded_image],
                    "stream": False
                }
                
                logging.debug(f"Sending image to vision model: {self.llava_model}")
                response = requests.post(f"{API_ENDPOINT}/api/generate", json=payload)
                
                if response.status_code == 200:
                    # Get the initial image description
                    initial_description = response.json().get("response", "")
                    logging.debug(f"Initial description length: {len(initial_description)}")
                    logging.debug(f"Initial description: {initial_description[:100]}...")
                    
                    # Use the description to generate a refined caption
                    prompt = f"{self.prompt_template}\n\n{initial_description}"
                    payload = {
                        "model": self.qwen_model,
                        "prompt": prompt,
                        "stream": False
                    }
                    
                    logging.debug(f"Sending to refiner model: {self.qwen_model}")
                    refine_response = requests.post(f"{API_ENDPOINT}/api/generate", json=payload)
                    
                    if refine_response.status_code == 200:
                        refined_result = refine_response.json().get("response", "")
                        logging.debug(f"Refined result length: {len(refined_result)}")
                        logging.debug(f"Refined result: {refined_result[:100]}...")
                        
                        # Ensure the result is a single line with no line breaks
                        refined_result = refined_result.replace("\n", " ").strip()
                        
                        # Apply custom format based on user preferences
                        prefix = self.custom_prefix if self.use_prefix else ""
                        suffix = self.custom_suffix if self.use_suffix else ""
                        formatted_result = f"{prefix}{refined_result}{suffix}"
                        
                        logging.debug(f"Formatted result length: {len(formatted_result)}")
                        logging.debug(f"Formatted result: {formatted_result[:100]}...")
                        
                        # Write the formatted result to a file
                        txt_path = os.path.join(IMAGES_FOLDER, f"{Path(file_name).stem}.txt")
                        with open(txt_path, "w") as txt_file:
                            txt_file.write(formatted_result)
                            logging.debug(f"Wrote formatted result to file: {txt_path}")
                    else:
                        logging.error(f"Error refining caption: {refine_response.text}")
                else:
                    logging.error(f"Error processing {file_name}: {response.text}")
            except Exception as e:
                logging.error(f"Exception processing image {image_path}: {str(e)}")

    def refine_captions(self):
        # This method is no longer needed
        pass

    def apply_custom_format(self):
        # This is now handled directly in caption_images
        pass


# Main Window
class CaptioningApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QIcon("logo/icon.ico"))
        self.setWindowTitle("LlmamaScribe by LamEmy | Revised & Upgraded by AngryHamster (Civitai)")
        self.setGeometry(100, 100, 600, 400)  # Increased size to accommodate new options
        self.source_folder = ""
        self.prompt_template = DEFAULT_PROMPT_TEMPLATE
        self.llava_model = ""
        self.qwen_model = ""
        
        # Custom prefix/suffix options
        self.use_prefix = True
        self.custom_prefix = DEFAULT_CAPTION_PREFIX
        self.use_suffix = True
        self.custom_suffix = DEFAULT_CAPTION_SUFFIX

        # Main layout with tabs
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Main tab
        self.main_tab = QWidget()
        self.init_main_tab()
        self.tabs.addTab(self.main_tab, "Main")

        # Advanced tab
        self.advanced_tab = QWidget()
        self.init_advanced_tab()
        self.tabs.addTab(self.advanced_tab, "Advanced")
        
        # Formatting tab
        self.formatting_tab = QWidget()
        self.init_formatting_tab()
        self.tabs.addTab(self.formatting_tab, "Formatting")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def init_main_tab(self):
        layout = QVBoxLayout()

        self.label = QLabel("Select a folder and click 'Start' to begin the captioning process.")
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Model Dropdowns
        model_group = QGroupBox("AI Models")
        model_layout = QGridLayout()
        
        self.vision_model_dropdown = QComboBox()
        self.refiner_model_dropdown = QComboBox()

        # Fetch and populate models
        installed_models = fetch_installed_models()
        self.vision_model_dropdown.addItems(installed_models)
        self.refiner_model_dropdown.addItems(installed_models)

        model_layout.addWidget(QLabel("Vision Model:"), 0, 0)
        model_layout.addWidget(self.vision_model_dropdown, 0, 1)

        model_layout.addWidget(QLabel("Refiner Model:"), 1, 0)
        model_layout.addWidget(self.refiner_model_dropdown, 1, 1)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        button_layout = QHBoxLayout()
        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_button)
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_captioning)
        button_layout.addWidget(self.start_button)

        layout.addLayout(button_layout)
        self.main_tab.setLayout(layout)

    def init_advanced_tab(self):
        layout = QVBoxLayout()

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("""Enter a custom system prompt here. This can be as simple or as complicated as you wish.
An example of a template prompt is:

You are an AI captioning expert. You will be provided with a description of an image and will refine it following this template: An image of a snow globe. The scene inside the snow globe shows (describe the scene).
The snow globe base is made of (describe what the snow globe base looks like). The text on the snow globe says (any detected text), (any further details not yet mentioned).

For further instructions on how to write a system prompt, see the readme.txt.""")
        self.prompt_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Always show vertical scrollbar

        layout.addWidget(QLabel("System Prompt:"))
        
        label = QLabel("Add any custom instructions in natural language.")
        label.setStyleSheet("border: 2px solid grey; background-color: rgba(169, 169, 169, 100);")  # grey with transparency
        layout.addWidget(label, alignment=Qt.AlignLeft)

        layout.addWidget(self.prompt_input)

        self.advanced_tab.setLayout(layout)
        
    def init_formatting_tab(self):
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Use this tab to customize the formatting of your captions. "
            "You can enable/disable the prefix and suffix, and customize their content."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Prefix options
        prefix_group = QGroupBox("Caption Prefix")
        prefix_layout = QVBoxLayout()
        
        self.use_prefix_checkbox = QCheckBox("Add prefix to captions")
        self.use_prefix_checkbox.setChecked(True)
        prefix_layout.addWidget(self.use_prefix_checkbox)
        
        self.prefix_input = QTextEdit()
        self.prefix_input.setPlainText(DEFAULT_CAPTION_PREFIX)
        self.prefix_input.setMaximumHeight(80)
        prefix_layout.addWidget(self.prefix_input)
        
        prefix_group.setLayout(prefix_layout)
        layout.addWidget(prefix_group)
        
        # Suffix options
        suffix_group = QGroupBox("Caption Suffix")
        suffix_layout = QVBoxLayout()
        
        self.use_suffix_checkbox = QCheckBox("Add suffix to captions")
        self.use_suffix_checkbox.setChecked(True)
        suffix_layout.addWidget(self.use_suffix_checkbox)
        
        self.suffix_input = QTextEdit()
        self.suffix_input.setPlainText(DEFAULT_CAPTION_SUFFIX)
        self.suffix_input.setMaximumHeight(80)
        suffix_layout.addWidget(self.suffix_input)
        
        suffix_group.setLayout(suffix_layout)
        layout.addWidget(suffix_group)
        
        # Help text
        help_text = QLabel(
            "Note: To permanently change the default prefix and suffix, modify the DEFAULT_CAPTION_PREFIX "
            "and DEFAULT_CAPTION_SUFFIX variables in the LlamaScribe.pyw file."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("font-style: italic; color: #666;")
        layout.addWidget(help_text)
        
        self.formatting_tab.setLayout(layout)
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.source_folder = folder
            self.label.setText(f"Selected Folder: {folder}")

    def start_captioning(self):
        self.llava_model = self.vision_model_dropdown.currentText()
        self.qwen_model = self.refiner_model_dropdown.currentText()

        # Use DEFAULT_PROMPT_TEMPLATE if prompt_input is empty or only whitespace
        entered_prompt = self.prompt_input.toPlainText().strip()
        self.prompt_template = entered_prompt if entered_prompt else DEFAULT_PROMPT_TEMPLATE
        
        # Get formatting options
        self.use_prefix = self.use_prefix_checkbox.isChecked()
        self.custom_prefix = self.prefix_input.toPlainText()
        self.use_suffix = self.use_suffix_checkbox.isChecked()
        self.custom_suffix = self.suffix_input.toPlainText()

        if not self.source_folder:
            self.label.setText("Error: Please select a folder first.")
            return

        self.worker = CaptioningWorker(
            self.source_folder,
            self.prompt_template,
            self.llava_model,
            self.qwen_model,
            self.use_prefix,
            self.custom_prefix,
            self.use_suffix,
            self.custom_suffix
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.process_finished)
        self.worker.start()

        self.label.setText("Captioning process started...")
        self.start_button.setEnabled(False)

    def update_progress(self, message, percentage):
        self.label.setText(message)
        self.progress_bar.setValue(percentage)

    def process_finished(self):
        self.label.setText("Captioning process completed successfully.")
        self.start_button.setEnabled(True)

# Entry point
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = CaptioningApp()
    window.show()
    sys.exit(app.exec_())
