import os
import numpy as np
import gradio as gr
import assemblyai as aai
from translate import Translator
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pathlib import Path


def voice_to_voice(audio_file):

    # transcript speech
    transcript = transcribe_audio(audio_file)

    if transcript.status == aai.TranscriptStatus.error:
        raise gr.Error(transcript.error)
    else:
        transcript = transcript.text

    # translate text
    list_translations = translate_text(transcript)
    generated_audio_paths = []

    # generate speech from text
    for translation in list_translations:
        translated_audio_file_name = text_to_speech(translation)
        path = Path(translated_audio_file_name)
        generated_audio_paths.append(path)


    return generated_audio_paths[0], generated_audio_paths[1], generated_audio_paths[2], generated_audio_paths[3], generated_audio_paths[4], generated_audio_paths[5], list_translations[0], list_translations[1], list_translations[2], list_translations[3], list_translations[4], list_translations[5]

# Function to transcribe audio using AssemblyAI
def transcribe_audio(audio_file):
    aai.settings.api_key = "<your-assemblyai-api-key>"

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    return transcript

    
# Function to translate text
def translate_text(text: str) -> str:

    languages = ["ru", "tr", "sv", "de", "es", "ja"]
    list_translations = []

    for lan in languages:
        translator = Translator(from_lang="en", to_lang=lan)
        translation = translator.translate(text)
        list_translations.append(translation)

    return list_translations

# Function to generate speech
def text_to_speech(text: str) -> str:

    # ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    client = ElevenLabs(
        api_key= "<your-elevenlabs-api-key>",
    )

    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        voice_id="<your-voice-id>", #clone your voice on elevenlabs dashboard and copy the id
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2", # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.8,
            style=0.5,
            use_speaker_boost=True,
        ),
    )

    save_file_path = f"{uuid.uuid4()}.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    return save_file_path


input_audio = gr.Audio(
    sources=["microphone"],
    type="filepath",
    show_download_button=True,
    waveform_options=gr.WaveformOptions(
        waveform_color="#01C6FF",
        waveform_progress_color="#0066B4",
        skip_length=2,
        show_controls=False,
    ),
)


with gr.Blocks() as demo:
    gr.Markdown("## Record yourself in English and immediately receive voice translations.")
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources=["microphone"],
                                type="filepath",
                                show_download_button=True,
                                waveform_options=gr.WaveformOptions(
                                    waveform_color="#01C6FF",
                                    waveform_progress_color="#0066B4",
                                    skip_length=2,
                                    show_controls=False,
                                ),)
            with gr.Row():
                submit = gr.Button("Submit", variant="primary")
                btn = gr.ClearButton(audio_input, "Clear")
                # btn.click(lambda: audio_input, None)

    with gr.Row():
        

        with gr.Group() as turkish:
            # gr.Image("flags/turkish.png", width = 150, show_download_button=False, show_label=False)
            tr_output = gr.Audio(label="Turkish", interactive=False)
            tr_text = gr.Markdown()

        with gr.Group() as swedish:
            # gr.Image("flags/swedish.png", width = 150, show_download_button=False, show_label=False)
            sv_output = gr.Audio(label="Swedish", interactive=False)
            sv_text = gr.Markdown()

        with gr.Group() as russian:
            # gr.Image("flags/russian.png", width = 150, show_download_button=False, show_label=False)
            ru_output = gr.Audio(label="Russian", interactive=False)
            ru_text = gr.Markdown()

    with gr.Row():

        with gr.Group():
            # gr.Image("flags/german.png", width = 150, show_download_button=False, show_label=False)
            de_output = gr.Audio(label="German", interactive=False)
            de_text = gr.Markdown()

        with gr.Group():
            # gr.Image("flags/spanish.png", width = 150, show_download_button=False, show_label=False)
            es_output = gr.Audio(label="Spanish", interactive=False)
            es_text = gr.Markdown()

        with gr.Group():
            # gr.Image("flags/japanese.png", width = 150, show_download_button=False, show_label=False)
            jp_output = gr.Audio(label="Japanese", interactive=False)
            jp_text = gr.Markdown()
                
    output_components = [ru_output, tr_output, sv_output, de_output, es_output, jp_output, ru_text, tr_text, sv_text, de_text, es_text, jp_text]
    submit.click(fn=voice_to_voice, inputs=audio_input, outputs=output_components, show_progress=True)
           
        
if __name__ == "__main__":
    demo.launch()
