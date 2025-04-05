import os
import hashlib
from typing import Dict
import azure.cognitiveservices.speech as speechsdk
from tutor.utils.anki import get_default_anki_media_dir

# Mapping of languages to Azure voice names
LANGUAGE_VOICE_MAP: Dict[str, str] = {
    "mandarin": "zh-CN-XiaoxiaoNeural",  # Mandarin female voice
    "cantonese": "zh-HK-HiuGaaiNeural",  # Cantonese female voice
    # Add more languages and voices as needed
}


def text_to_speech(text: str, language: str) -> str:
    """Convert text to speech using Azure Text-to-Speech service.

    Args:
        text: The text to convert to speech
        language: The language of the text (e.g., 'mandarin', 'cantonese')

    Returns:
        Path to the generated audio file
    """
    speech_key = os.environ.get("AZURE_SPEECH_SERVICE_KEY")
    service_region = os.environ.get("AZURE_SPEECH_SERVICE_REGION")

    # Initialize the speech config
    speech_config = speechsdk.SpeechConfig(speech_key, service_region)

    # Set the voice based on the language
    language = language.lower()
    if language not in LANGUAGE_VOICE_MAP:
        raise ValueError(
            f"Unsupported language: {language}. Supported languages are: {', '.join(LANGUAGE_VOICE_MAP.keys())}"
        )
    voice_name = LANGUAGE_VOICE_MAP[language]

    speech_config.speech_synthesis_voice_name = voice_name

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
        from tutor.utils.logging import dprint

        dprint(f"Speech synthesis succeeded. Audio saved to: {filename}")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        from tutor.utils.logging import dprint

        dprint(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            dprint(f"Error details: {cancellation_details.error_details}")

    return filename
