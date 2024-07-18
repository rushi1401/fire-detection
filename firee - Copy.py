import streamlit as st
import cv2
import numpy as np
from pytube import YouTube
from twilio.rest import Client
import tempfile
import os
from ultralytics import YOLO
import cvzone
import math

# Twilio configuration
account_sid = 'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
auth_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
client = Client(account_sid, auth_token)
from_whatsapp_number = 'whatsapp:+1400000'  # Use the Twilio Sandbox WhatsApp number
to_whatsapp_number = 'whatsapp:+910000000'   # Your WssssshatsApp number (ensure you have joined the sandbox)

def send_whatsapp_message(message):
    try:
        message = client.messages.create(body=message, from_=from_whatsapp_number, to=to_whatsapp_number)
        st.success(f"Message sent: SID {message.sid}")
    except Exception as e:
        st.error(f"Failed to send message: {e}")

# Load YOLO
model = YOLO('fire_model.pt')

# Reading the classes
classnames = ['fire']

def detect_fire(frame, confidence_threshold=50):
    result = model(frame, stream=True)
    fire_detected = False  # Flag to check if fire is detected

    for info in result:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            Class = int(box.cls[0])
            if confidence > confidence_threshold:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                cvzone.putTextRect(frame, f'{classnames[Class]} {confidence}%', [x1 + 8, y1 + 100], scale=1.5, thickness=2)
                fire_detected = True  # Set flag to True if fire is detected

    return fire_detected, frame

# Streamlit UI
st.title("Risk Analyser")

# Sidebar
st.sidebar.header("Choose Input Type")
input_type = st.sidebar.radio("Input Type", ["Image Footage", "Video", "CCTV", "YouTube"])
human_count = st.sidebar.empty()  # Placeholder for human count display
risk_detected = st.sidebar.empty()  # Placeholder for risk detection display

if input_type == "Image Footage":
    st.sidebar.markdown("---")
    uploaded_image = st.sidebar.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    st.sidebar.markdown("**Developed By Rajyug Solutions Ltd.**")
    if uploaded_image:
        # Process the uploaded image
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        # Process the image here
elif input_type == "Video":
    st.sidebar.markdown("---")
    uploaded_video = st.sidebar.file_uploader("Upload Video", type=["mp4", "avi"])
    st.sidebar.markdown("**Developed By Rajyug Solutions Ltd.**")
    if uploaded_video:
        # Process the uploaded video
        st.video(uploaded_video)
        temp_video_file = tempfile.NamedTemporaryFile(delete=False)
        temp_video_file.write(uploaded_video.read())
        temp_video_file.flush()
        cap = cv2.VideoCapture(temp_video_file.name)
        
        if not cap.isOpened():
            st.error("Error: Could not open video file")
            exit()

        alert_sent = False
        fire_alert_sent = False

        confidence_threshold = 50

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            fire_detected, frame = detect_fire(frame, confidence_threshold)

            # Display risk detection status
            risk_detected_status = "Yes" if fire_detected else "No"
            risk_detected.markdown(f"**Risk Detected:** {risk_detected_status}")

            if fire_detected and not fire_alert_sent:
                st.write("Fire detected, sending alert...")
                send_whatsapp_message('Fire detected in the video!')
                fire_alert_sent = True

            # Convert frame to bytes for displaying in Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.image(frame_rgb, channels="RGB")

        cap.release()
        os.remove(temp_video_file.name)
elif input_type == "CCTV":
    st.sidebar.markdown("---")
    cctv_url = st.sidebar.text_input("Enter CCTV URL")
    st.sidebar.markdown("**Developed By Rajyug Solutions Ltd.**")
    if cctv_url:
        st.write("CCTV URL:", cctv_url)
        # Process the CCTV stream here
elif input_type == "YouTube":
    st.sidebar.markdown("---")
    youtube_url = st.sidebar.text_input("Enter YouTube URL")
    st.sidebar.markdown("**Developed By Rajyug Solutions Ltd.**")
    if youtube_url:
        st.write("YouTube URL:", youtube_url)
        if st.button("Analyse Risk"):
            try:
                yt = YouTube(youtube_url)
                video = yt.streams.filter(file_extension='mp4').first()
                temp_video_file = tempfile.NamedTemporaryFile(delete=False)
                video.download(filename=temp_video_file.name)

                st.video(temp_video_file.name)

                cap = cv2.VideoCapture(temp_video_file.name)
                if not cap.isOpened():
                    st.error("Error: Could not open video file")
                    exit()

                alert_sent = False
                fire_alert_sent = False

                confidence_threshold = 50

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    fire_detected, frame = detect_fire(frame, confidence_threshold)

                    # Display risk detection status
                    risk_detected_status = "Yes" if fire_detected else "No"
                    risk_detected.markdown(f"**Risk Detected:** {risk_detected_status}")

                    if fire_detected and not fire_alert_sent:
                        st.write("Fire detected, sending alert...")
                        send_whatsapp_message('Fire detected in the video!')
                        fire_alert_sent = True

                    # Convert frame to bytes for displaying in Streamlit
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.image(frame_rgb, channels="RGB")

                cap.release()
                os.remove(temp_video_file.name)
            except Exception as e:
                st.error(f"An error occurred: {e}")
