# Extractify 🔍
**Extractify** is an application designed to extract relevant details such as business name, address, TIN number, date, and total cost from images of official receipts using Optical Character Recognition (OCR) and Large Language Models (LLMs). The app supports both real-time image capture from a webcam and image uploads, making it easy to digitize receipts for personal or business needs.

## Features 💻
- Real-time Image Capture: Capture images using your device's webcam to extract text.
Image Upload: Upload receipt images from your device to extract relevant details.
- Google Generative AI Integration: Automatically processes the OCR-extracted text using the Gemini model to identify and format the receipt details (e.g., address, business name, TIN number, etc.).
- PaddleOCR Integration: Uses PaddleOCR for robust text extraction from receipt images.

## Technologies Used ⚙️
Python
Flet: For building the UI.
OpenCV: For capturing images from the webcam and image processing.
PaddleOCR: For Optical Character Recognition (OCR).
Google Generative AI (Gemini Model): For extracting and formatting key details from the OCR results.
PIL (Pillow): For image processing and conversion.
NumPy: For handling image data.
Threading: For running background tasks such as webcam feed capture.

## Installation
### Prerequisites
1. Google Cloud API key (for Google Generative AI) - Get your API from [Google AI Studio](https://ai.google.dev/aistudio)
1. Clone the Repository
```bash
git clone https://github.com/yourusername/extractify.git
cd extractify
```
2. Set Up Your Environment
```bash
python -m venv .env
```
3. Install Dependencies
``` bash
pip install -r requirements.txt
```
4. Set up your Google API key by exporting it in your environment:
Get your API from [Google AI Studio](https://ai.google.dev/aistudio)
```bash
export API_KEY="your-google-api-key"
```

## How to Run 🏃‍♂️‍➡️
After completing the setup, you can start the application by running the following command:
```bash
flet run
```
Once the app starts, you can:

- Take a Picture: Use your device’s webcam to capture an image of your receipt.
- Upload an Image: Upload an image file of a receipt from your local machine.
- Extract Details: Extract key details like address, business name, TIN number, date, and total cost from the image.

## Project Structure 🏗️
```bash
Extractify/
│
├── main.py                # Main entry point for the application.
├── requirements.txt        # List of required dependencies.
├── README.md               # Project documentation.
├── youphoto/               # Folder to store captured and processed images. (deletes the image immediately after processing)
└── .env                    # (optional) Environment variables for sensitive data (API keys).
```
## Known Issues ❌
- The webcam may fail to capture a frame on certain systems. If you encounter this issue, check your camera permissions and drivers.
- Ensure PaddleOCR's language model (en) is downloaded when running the app for the first time.
- Flet does not currently suppport file uploads on web view.

## Future Improvements ✅
- Improve the UI experience, such as real-time bounding box updates during live feed.
- Enhance error handling and logging.
  
## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any features or bug fixes you'd like to propose.
