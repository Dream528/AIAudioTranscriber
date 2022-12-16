import streamlit as st
import streamlit_lottie
import whisper
import pathlib

from utils import *

def main():
    """
    Main Function
    """
    st.set_page_config(
        page_title="AI Audio Transciber",
        page_icon="▶️",
        layout= "centered",
        menu_items={
        'Get Help': 'https://github.com/smaranjitghose/AIAudioTranscriber',
        'Report a bug': "https://github.com/smaranjitghose/AIAudioTranscriber/issues",
        'About': "## A minimalistic application to generate transcriptions for audio built using Python"
        } )
    
    st.title("AI Audio Transcriber")
    hide_footer()
    # Load and display animation
    anim = lottie_local("assets/animations/transcriber.json")
    st_lottie(anim,
            speed=1,
            reverse=False,
            loop=True,
            quality="medium", # low; medium ; high
            # renderer="svg", # canvas
            height=400,
            width=400,
            key=None)
    # Initialize Session State Variables
    if "page_index" not in st.session_state:
        st.session_state["file_path"] = ""
        st.session_state["transcript"] = ""
        st.session_state["page_index"] = 0
    # Component for uploading an audio file of the format .wav,.mp3 or.m4a
    st.sidebar.markdown("### Upload your audio file 📁")
    uploaded_file = st.sidebar.file_uploader(
            label="Upload your file 📁",
            type=["wav","mp3","m4a"],
            accept_multiple_files=False,
            label_visibility="hidden"
            )
    # As soon as a relevant audio file is uploaded
    if uploaded_file is not None:
        # Create an inputs sub-directory if it does not exist already
        APP_DIR = pathlib.Path(__file__).parent.absolute()
        INPUT_DIR = APP_DIR / "input"
        INPUT_DIR.mkdir(exist_ok=True)
        # Extract file format
        upload_name = uploaded_file.name
        upload_format = upload_name.split(".")[-1]
        # Create final input path
        input_name = f"audio.{upload_format}"
        st.session_state["file_path"] = INPUT_DIR / input_name
        # Save the input audio file to server
        with open(st.session_state["file_path"], "wb") as f:
                    f.write(uploaded_file.read())    

    st.sidebar.markdown("---")    
    model_type = st.sidebar.radio(label="Choose Model Version",
                    options=["base","small","medium"])
    
    # When the client clicks on Button to produce output
    if st.sidebar.button("Generate✨"):
        if uploaded_file is not None:
            # load audio and pad/trim it to fit 30 seconds
            audio = whisper.load_audio(st.session_state["file_path"])
            audio = whisper.pad_or_trim(audio)
            # Load the model
            model = get_model(model_type)
            # make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            # detect the spoken language
            _, probs = model.detect_language(mel)
            lang = max(probs, key=probs.get)
            # Pass the audio file to the model and generate transcripts
            result = model.transcribe(audio)
            st.balloons()
            # Grab the text and update it in session state for the app
            st.session_state["transcript"] = result["text"]

            col1,col2 = st.columns(2,gap ="small")
            # Display the generated Transcripts
            with col1:
                st.markdown("## Output ")
                st.markdown(f"**Detected language🌐**: {lang}")
                st.markdown("**Generated Transcripts** 📃: ")
                st.markdown(st.session_state["transcript"])
                        # Display the original Audio
            with col2:
                st.markdown("## Original Audio ▶️")
                st.audio(uploaded_file)
                # Download button
                st.download_button(
                            label="Download Transcripts📥",
                            data = st.session_state["transcript"],
                            file_name="transcripts.txt",
                            mime = "text/plain")
        else:
            st.error("Please upload an audio file 🙏")

@st.cache
def get_model(model_type:str):
        model = whisper.load_model(model_type)
        return model


if __name__ == "__main__":
    main()