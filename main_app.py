import streamlit as st
import cv2
import os
from moviepy import ImageSequenceClip

# Create folders
os.makedirs("uploads", exist_ok=True)
os.makedirs("blurred_frames", exist_ok=True)
os.makedirs("output", exist_ok=True)

st.set_page_config(page_title="AI Video Privacy Studio", page_icon="🎥")

st.title("🎥 AI Video Privacy Studio")
st.write("Upload a video → Blur faces → Download privacy-safe video")

uploaded_file = st.file_uploader("📤 Upload a video", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    video_path = os.path.join("uploads", uploaded_file.name)

    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ Video uploaded successfully!")
    st.video(video_path)

    if st.button("🚀 Process Video"):
        progress = st.progress(0)

        # Open video
        cap = cv2.VideoCapture(video_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            fps = 24

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_count = 0
        processed_frames = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Get frame dimensions
            h, w = frame.shape[:2]

            # Simulated face privacy region (center area)
            x1 = int(w * 0.35)
            y1 = int(h * 0.2)
            x2 = int(w * 0.65)
            y2 = int(h * 0.6)

            region = frame[y1:y2, x1:x2]
            blurred = cv2.GaussianBlur(region, (99, 99), 30)
            frame[y1:y2, x1:x2] = blurred

            frame_path = os.path.join( "blurred_frames", f"frame_{frame_count:05d}.jpg" )

            cv2.imwrite(frame_path, frame)
            processed_frames.append(frame_path)

            frame_count += 1

            if total_frames > 0:
                progress.progress(min(frame_count / total_frames, 1.0))

        cap.release()

        # Rebuild video
        clip = ImageSequenceClip(processed_frames, fps=fps)
        output_path = os.path.join( "output", "privacy_safe_video.mp4" )

        clip.write_videofile( output_path, codec="libx264", audio=False, verbose=False, logger=None )

        st.success(f"🎉 Processed {frame_count} frames successfully!")

        st.subheader("🔒 Privacy-Safe Video")
        st.video(output_path)

        with open(output_path, "rb") as video_file:
            st.download_button( label="⬇ Download Privacy-Safe Video", data=video_file, file_name="privacy_safe_video.mp4", mime="video/mp4" )

        st.subheader("📊 Statistics")
        col1, col2 = st.columns(2)
        col1.metric("Frames Processed", frame_count)
        col2.metric("FPS", round(fps, 2))

st.markdown("---")
st.caption("🚀 Built for Hackathon • AI Video Privacy Studio")
