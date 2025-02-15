import os
import hashlib
import azure.cognitiveservices.speech as speechsdk
from tutor.utils.anki import get_default_anki_media_dir


def text_to_speech(text):
    speech_key = os.environ.get("AZURE_SPEECH_SERVICE_KEY")
    service_region = os.environ.get("AZURE_SPEECH_SERVICE_REGION")

    # Initialize the speech config
    speech_config = speechsdk.SpeechConfig(speech_key, service_region)

    # Set the voice for Mandarin Chinese
    speech_config.speech_synthesis_voice_name = (
        "zh-CN-XiaoxiaoNeural"  # Example voice, Mandarin female
    )

    # Configure the output to save to a file
    filename = str(
        get_default_anki_media_dir()
        / f"chinese-tutor-{hashlib.md5(text.encode()).hexdigest()}.wav"
    )
    audio_output = speechsdk.audio.AudioOutputConfig(filename=filename)

    # Create a speech synthesizer with audio output
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_output
    )

    # Perform speech synthesis
    result = synthesizer.speak_text_async(text).get()

    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesis succeeded. Audio saved to: {filename}")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

    return filename
