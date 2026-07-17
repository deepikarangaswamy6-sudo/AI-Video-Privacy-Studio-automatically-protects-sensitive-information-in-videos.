import streamlit as st
import cv2
import os
import numpy as np
from moviepy import ImageSequenceClip

# ----------------------------
# Create required folders
# ----------------------------
os.makedirs("uploads", exist_ok=True)
os.makedirs("blurred_frames", exist_ok=True)
os.makedirs("output", exist_ok=True)

# ----------------------------
# Streamlit Page Settings
# ----------------------------
st.set_page_config( page_title="AI Video Privacy Studio", page_icon="🎥", layout="wide" )

st.title("🎥 AI Video Privacy Studio")
st.markdown("### Extract Frames • Blur Faces • Rebuild Privacy-Safe Video")
st.markdown("---")

# ----------------------------
# Upload Video
# ----------------------------
uploaded_file = st.file_uploader( "📤 Upload a video", type=["mp4", "mov", "avi"] )

if uploaded_file is not None:
    # Save uploaded video
    video_path = os.path.join("uploads", uploaded_file.name)

    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ Video uploaded successfully!")
    st.video(video_path)

    # ----------------------------
    # Process Button
    # ----------------------------
    if st.button("🚀 Process Video"):
        progress = st.progress(0)
        status = st.empty()

        # Load face detector
        cascade_path = os.path.join( cv2.__path__[0], "data", "haarcascade_frontalface_default.xml" )
face_cascade = cv2.CascadeClassifier(cascade_path)

        # Open video
        cap = cv2.VideoCapture(video_path)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        if fps == 0:
            fps = 24

        frame_count = 0
        processed_frames = []

        status.text("🔍 Detecting and blurring faces...")

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale( gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30) )

            # Blur each detected face
            for (x, y, w, h) in faces:
                face_region = frame[y:y+h, x:x+w]
                blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
                frame[y:y+h, x:x+w] = blurred_face

            # Save processed frame
            frame_path = os.path.join( "blurred_frames", f"frame_{frame_count:05d}.jpg" )

            cv2.imwrite(frame_path, frame)
            processed_frames.append(frame_path)

            frame_count += 1

            # Update progress bar
            if total_frames > 0:
                progress.progress(min(frame_count / total_frames, 1.0))

        cap.release()

        status.text("🎬 Rebuilding privacy-safe video...")

        # ----------------------------
        # Create video from processed frames
        # ----------------------------
        clip = ImageSequenceClip(processed_frames, fps=fps)

        output_path = os.path.join( "output", "privacy_safe_video.mp4" )

        clip.write_videofile( output_path, codec="libx264", audio=False, verbose=False, logger=None )

        progress.progress(1.0)
        status.text("✅ Processing completed!")

        st.success(f"🎉 Successfully processed {frame_count} frames")

        # ----------------------------
        # Show output video
        # ----------------------------
        st.subheader("🔒 Privacy-Safe Output Video")
        st.video(output_path)

        # ----------------------------
        # Download button
        # ----------------------------
        with open(output_path, "rb") as video_file:
            st.download_button( label="⬇️ Download Privacy-Safe Video", data=video_file, file_name="privacy_safe_video.mp4", mime="video/mp4" )

        # ----------------------------
        # Statistics Dashboard
        # ----------------------------
        st.markdown("---")
        st.subheader("📊 Processing Statistics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Frames Processed", frame_count)

        with col2:
            st.metric("FPS", round(fps, 2))

        with col3:
            st.metric("Privacy Status", "Protected")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.caption("🚀 Built for Hackathon • AI Video Privacy Studio")
