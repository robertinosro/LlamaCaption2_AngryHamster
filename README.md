# LlamaScribe by LamEmy | Revised & Upgraded by AngryHamster (Civitai)
Originally developed by https://civitai.com/user/LamEmy
revised and upgraded by https://civitai.com/user/AngryHamster

LlamaScribe is a GUI-based image captioning tool that uses local AI models to generate customized captions for images.

## Features

- Process multiple images in a batch
- Generate AI-powered image descriptions
- Apply custom formatting to captions
- User-friendly interface
- Works with local Ollama models

LlamaScribe processes images by:

copying contents of the folder you select
Converts images to png
Generating Captions using an AI Vision Model (e.g., LLaVA).
Refining Captions using an optional Refiner Model (e.g., Qwen) while following instructions you typed in to the advanced tab.
Adding Custom Prefix/Suffix Text to tailor captions. (trigger words for loras)
The tool outputs image captions as .txt files alongside the copied images in a newly created folder called "Processed_images_with_captions" . It names the .txt files with the same name as the corresponding image. This makes it ideal for use with the civitai onsite model trainer. you can just compress the images and .txt files in to a zip file and drag the zip file in to the civitai trainer, The site will show all images with the captions attached. This is also the same format required for ostris's ai-toolkit and most locally run lora trainers.

## Requirements

- Windows operating system
- [Ollama](https://ollama.ai/) installed and running locally (https://ollama.com/library/llama3.2-vision)
- A compatible vision model (like llava) for image analysis
- A compatible text model (like qwen) for caption refinement


## Installation

1. Download the latest release
2. Extract the files to a location of your choice
3. Make sure Ollama is installed and running
4. Run `LlamaScribe.exe`
5. Requirements txt is not needed ( unless you plan to edit/modify the code/exe file)

Linux/MacOS:
Ollama: install by going to https://ollama.com/ download and follow the instructions.
Once Ollama is installed you need to install your choice of models. you can select from available models here: https://ollama.com/search, to install a model once chosen open a cmd window and type "ollama run (model name)" e.g. "ollama run llava" 
You need 1 of any vision model: https://ollama.com/search?c=vision (recommended to use llava as is lightweight and fast.)
You then can select any optional language model as a refiner model:  https://ollama.com/search (you can use llava again but I recommend qwen or llama3 for best results. if just wanting basic captioning just llava is fine but better results can be acheived)

## Usage

1. Launch the application by running `LlamaScribe.exe`
2. Select a folder containing images you want to caption
3. Choose your preferred vision and text models from the dropdown menus
4. Click "Start" to begin the captioning process
5. Captions will be saved as text files alongside your images in the `Processed_images_with_captions` folder

Outputs
Captions are saved as .txt files alongside the images in a new folder named "Processed_images_with_captions", The newly created folder will be in the same location as the .exe and .pwy launchers:
files inside the new folder will be structured like so:
├── image1.png
├── image1.txt
├── image2.png
├── image2.txt

## Custom Note: running the captioner will replace the "Processed_images_with_captions" with the new results, deleting the old images and captions. this is by design to save memory space. Make sure to copy outputs to a different location before running again, (anywhere other than the "Processed_images_with_captions" folder) to keep the previously generated captions)

## Custom Caption Formatting

LlamaScribe now offers flexible caption formatting options through the dedicated "Formatting" tab:

- **Enable/Disable Prefix**: Choose whether to add a prefix to your captions
- **Enable/Disable Suffix**: Choose whether to add a suffix to your captions
- **Custom Prefix/Suffix**: Modify the content of both the prefix and suffix

The default formatting applies:
1. Prefix: "A photo of a woman, bloobikkx1, curvy blonde with (a well-defined neck:1.3) and (natural proportions:1.2), "
2. AI-generated image description in the middle
3. Suffix: " (masterpiece, ultra-realistic, high-definition, 8K, cinematic lighting),(professional photography:1.4), (sharp focus:1.2), (studio lighting:1.2), (clear details:1.3), (professional atmosphere:1.3)"

You can customize both the prefix and suffix directly in the application without modifying the source code. Your changes will be applied to all processed images in the current session.

### Tips for Caption Formatting

- Use the prefix checkbox to establish the subject and basic attributes
- Use the suffix checkbox to add style modifiers and quality enhancements
- For permanent changes to the defaults, modify the `DEFAULT_CAPTION_PREFIX` and `DEFAULT_CAPTION_SUFFIX` constants in the source code

## Advanced Options

Step 4: Advanced Tab (optional and for advanced users)
Enter a Custom Prompt for the refiner model. Example:
You are an AI captioning expert. Describe the image in extreme detail, describe only what can be seen in the image and nothing else.  

Ollama Local API Endpoints
The script connects to the local ollama api server at http://localhost:11434/api/generate. This is the default when installing ollama, if you have issues with the programme connecting to the local endpoint check you are running ollama, click start menu, type ollama, click ollama application. ### OLLAMA MUST BE RUNNING FOR LLAMASCRIBE TO WORK!!! ###

## Changing Ollama API Endpoint:
If you wish to change where the API Endpoint is running, as of LlamaScribe v1.2 and above, you can now open the config.txt where you can edit the line API_ENDPOINT=http://localhost:11434 replace the url with your endpoint url. This will now work for both python file and .exe users. This is intended for any users running ollama on second machines and anyone who has changed the default location. If you have any issues with this feature please let me know and I will see what I can do to help. This is an advanced feature and is intentionally not included in the UI to avoid issues.

## Development

If you want to modify the application:

1. The main script is `LlamaScribe.pyw`
2. You can run it directly with Python (requires PyQt5, requests, and Pillow)
3. To build the executable, use PyInstaller:
   ```
   python -m PyInstaller --onefile --windowed --icon=logo/icon.ico --hidden-import=PyQt5 --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui LlamaScribe.pyw
   ```

## Best Practices
Ensure High-Quality Images:
Clear, high-resolution images improve caption accuracy and overall lora training.

Use Consistent Model Pairing:
Use LLaVA for captioning or any vision model, and Qwen or any llm for refining to get the best results. Although there are other models that pair well together such as llava and llama3.2. Its really a matter of what you prefer and what your system can run. Just play around with the models and see what works best. Note quality of results are dependant on the quality of the ai model, the better the models the better the captions and instruction following.

Write Clear Custom Instructions:
Be specific about the captioning style or details you want, Just tell it directly what its aim is, give it a template it should follow, tell it words you don't want included in captions.

Test Small Batches:
Start with a small folder of images to ensure everything works correctly before running on large datasets.

## Verify API Availability:
You can confirm that the API server is running and models are available by typing this in to a cmd window:
curl http://localhost:11434/api/tags 
If running in the correct location you should see a list of installed model names, if you get an error message then you are likely not running ollama or have changed default ollama setting.

## License

This project is open source and available for personal and commercial use.

## Acknowledgments

- Built with PyQt5 for the user interface
- Uses Ollama for local AI model inference
- Icon and logo design custom created
"# LlamaScribeTool_AngryHamster" 
"# LlamaCaption2_AngryHamster" 
