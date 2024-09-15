import flet as ft
import cv2
import time
import os
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import threading
import google.generativeai as genai

# Cache the OCR model outside the main function
ocr = PaddleOCR(use_angle_cls=True, lang='en')

genai.configure(api_key=os.environ["API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

# Function to convert image (numpy array) to base64 string
def convert_image_to_base64(image_np):
    image_pil = Image.fromarray(image_np)
    buffer = BytesIO()
    image_pil.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Function to create a placeholder image using numpy (e.g., white image)
def create_placeholder_image():
    placeholder_np = np.ones((800, 800, 3), dtype=np.uint8) * 255  # White 300x300 image
    placeholder_img = Image.fromarray(placeholder_np)
    buffer = BytesIO()
    placeholder_img.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def main(page: ft.Page):
    page.scroll = ft.ScrollMode.ALWAYS
    page.update()

    # Show placeholder image initially
    myimage = ft.Image(
        src_base64=create_placeholder_image(),
        width=700,
        height=400,
        fit="cover"
    )

    # Text widget to display OCR results
    ocr_text = ft.Column([])

    # Variable to store webcam status (whether it's live or not)
    live_feed_running = [False]  # Use a list to pass by reference

    loading_indicator = ft.ProgressRing(visible=False)

    def show_loading():
        loading_indicator.visible = True
        page.update()

    def hide_loading():
        loading_indicator.visible = False
        page.update()


    # Remove all images in the 'youphoto' folder
    def removeallyouphoto():
        folder_path = "youphoto/"
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File removed: {file_path}")

    # Function to continuously capture the live feed and update the UI
    def start_live_feed():
        # Change webcam resolution
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Failed to open the webcam.")
            return

        live_feed_running[0] = True

        while live_feed_running[0]:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Convert BGR to RGB to fix the color issue
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Update the live feed image in the app
            img_base64 = convert_image_to_base64(frame_rgb)
            myimage.src_base64 = img_base64
            page.update()

        cap.release()

    # Function to capture a picture when the "Take My Face" button is clicked
    def capture_picture(e):
        show_loading()
        # Disable the "Take My Face" button to prevent multiple clicks
        take_picture_button.disabled = True
        page.update()

        removeallyouphoto()

        # Stop the live feed if it's running
        live_feed_running[0] = False

        # Open the webcam to capture the current frame
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Failed to open the webcam.")
            hide_loading()
            take_picture_button.disabled = False
            page.update()
            return

        # Capture a single frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from webcam.")
            cap.release()
            hide_loading()
            take_picture_button.disabled = False
            page.update()
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        timestamp = str(int(time.time()))
        folder_path = "youphoto/"
        myfileface = f"myCapturedFace_{timestamp}.jpg"
        Image.fromarray(frame_rgb).save(f"{folder_path}{myfileface}")

        result = ocr.ocr(f"{folder_path}{myfileface}", cls=True)
        image_np = np.array(Image.open(f"{folder_path}{myfileface}").convert("RGB"))
        
        ocr_text.controls.clear()
        strings = []
        if not result or not result[0]:
            ocr_text.controls.append(ft.Text("No text detected", size=20, weight="bold"))
        else:
            for line in result:
                for word_info in line:
                    box = np.array(word_info[0], dtype=np.int32)
                    text_str = word_info[1][0]
                    strings.append(text_str)
                    cv2.polylines(image_np, [box], isClosed=True, color=(0, 255, 0), thickness=2)
        details = " ".join(strings)
        response = model.generate_content(f"Find the name of the business name, its address, TIN Number, Date, and Total cost of an Official Receipt. \
                                            The format should be like this: Address: Address Extracted, Business: (Business Name Extracted), TIN: (TIN Number Extracted), Date: (Date Extracted), Total: (Total Cost Extracted). New lines should be in between the details  \
                                                If something is not available, just put N/A. \
                                            Give the answer straight away and no other response besides the answer. : {details}").text
        text = ft.Text(response, size=20, weight="bold")
        ocr_text.controls.append(text)
        image_with_boxes_pil = Image.fromarray(image_np)
        image_with_boxes_pil.save(f"{folder_path}{myfileface}")

        img_base64 = convert_image_to_base64(image_np)
        myimage.src_base64 = img_base64

        retake_button.visible = True
        ocr_text.visible = True

        take_picture_button.disabled=True
        hide_loading()

        page.update()
        cap.release()

    # Function to handle uploaded files
    def file_uploaded(e: ft.FilePickerResultEvent):
        show_loading()
        if e.files:
            file_path = e.files[0].path
            print(f"File uploaded: {file_path}")

            try:
                # Ensure the image is loaded and converted correctly
                image_pil = Image.open(file_path)
                image_np = np.array(image_pil.convert("RGB"))  # Convert to RGB format for OCR

                # Remove any previous photo in the folder
                removeallyouphoto()

                folder_path = "youphoto/"
                myfileface = f"capture.jpg"
                image_pil.save(f"{folder_path}{myfileface}")

                # Perform OCR on the uploaded image
                result = ocr.ocr(file_path, cls=True)

                # Clear previous OCR text
                ocr_text.controls.clear()
                strings = []
                if not result or not result[0]:
                    ocr_text.controls.append(ft.Text("No text detected", size=20, weight="bold"))
                else:
                    for line in result:
                        for word_info in line:
                            box = np.array(word_info[0], dtype=np.int32)
                            text_str = word_info[1][0]
                            strings.append(text_str)
                            cv2.polylines(image_np, [box], isClosed=True, color=(0, 255, 0), thickness=2)

                details = " ".join(strings)
                response = model.generate_content(f"Find the name of the business name, its address, TIN Number, Date, and Total cost of an Official Receipt. \
                                                    The format should be like this: Address: Address Extracted, Business: (Business Name Extracted), TIN: (TIN Number Extracted), Date: (Date Extracted), Total: (Total Cost Extracted). New lines should be in between the details  \
                                                        If something is not available, just put N/A. \
                                                    Give the answer straight away and no other response besides the answer. : {details}").text
                text = ft.Text(response, size=20, weight="bold")
                ocr_text.controls.append(text)

                # Save and display the uploaded image with bounding boxes
                image_with_boxes_pil = Image.fromarray(image_np)
                image_with_boxes_pil.save(f"{folder_path}{myfileface}")

                # Update the image in the UI
                img_base64 = convert_image_to_base64(image_np)
                myimage.src_base64 = img_base64
                ocr_text.visible = True
                page.update()

            except Exception as ex:
                print(f"Error processing file: {ex}")
                ocr_text.controls.append(ft.Text("Error processing file", size=20, weight="bold"))
                page.update()
        hide_loading()

    # Function to retake the picture and restart the live feed
    def retake_picture(e):
        ocr_text.controls.clear() 
        ocr_text.visible = False 
        retake_button.visible = False  

        take_picture_button.disabled = False

        live_feed_running[0] = True
        start_feed_thread()

        page.update()

    # Start the live feed in a separate thread to avoid blocking the UI
    def start_feed_thread():
        feed_thread = threading.Thread(target=start_live_feed, daemon=True)
        feed_thread.start()

    # File picker for uploading images
    file_picker = ft.FilePicker(on_result=file_uploaded)

    take_picture_button = ft.ElevatedButton("Take a Picture", bgcolor="blue", color="white", on_click=capture_picture)
    retake_button = ft.ElevatedButton("Retake", bgcolor="red", color="white", on_click=retake_picture, visible=False)
    upload_button = ft.ElevatedButton("Upload Image", on_click=lambda _: file_picker.pick_files(allow_multiple=False))

    page.add(
        ft.Row([
            ft.Column([
                ft.Text("Extractify 🔍", size=30, weight="bold"),
                ft.Text("Extract text from your receipts for your digital needs.", size=20, color="gray"),
                take_picture_button,
                upload_button,  # Add the upload button here
                loading_indicator,
                myimage,
                retake_button, 
                ft.Container(ocr_text, padding=10, width=600, height=200)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

    # Register file picker with the page
    page.overlay.append(file_picker)

    # Start the live feed when the page starts
    start_feed_thread()

# Run the Flet app
ft.app(target=main)
