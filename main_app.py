import streamlit as st
import cv2
import os
from moviepy import ImageSequenceClip

# Create folders
os.makedirs("uploads", exist_ok=True)
os.makedirs("frames", exist_ok=True)
os.makedirs("blurred_frames", exist_ok=True)
os.makedirs("output", exist_ok=True)

st.set_page_config(page_title="AI Video Privacy Studio", page_icon="🎥")
st.title("🎥 AI Video Privacy Studio")
st.write("Extract frames → Blur faces → Rebuild privacy-safe video")

uploaded = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

if uploaded:
    video_path = f"uploads/{uploaded.name}"
    with open(video_path, "wb") as f:
        f.write(uploaded.read())

    st.success("Video uploaded successfully!")

    if st.button("🚀 Process Video"):
        cap = cv2.VideoCapture(video_path)
        face_cascade = cv2.CascadeClassifier( cv2.data.haarcascades + "haarcascade_frontalface_default.xml" )

        frame_count = 0
        processed_files = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            # Blur detected faces
            for (x, y, w, h) in faces:
                face = frame[y:y+h, x:x+w]
                face = cv2.GaussianBlur(face, (99, 99), 30)
                frame[y:y+h, x:x+w] = face

            out_path = f"blurred_frames/frame_{frame_count:04d}.jpg"
            cv2.imwrite(out_path, frame)
            processed_files.append(out_path)
            frame_count += 1

        cap.release()

        st.success(f"Processed {frame_count} frames")

        # Rebuild video
        clip = ImageSequenceClip(processed_files, fps=24)
        output_path = "output/privacy_safe_video.mp4"
        clip.write_videofile(output_path, codec="libx264", audio=False)

        st.success("Privacy-safe video created!")
        st.video(output_path)

        with open(output_path, "rb") as f:
            st.download_button( "⬇ Download Privacy-Safe Video", f, file_name="privacy_safe_video.mp4" )
