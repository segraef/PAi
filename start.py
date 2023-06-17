import azure.cognitiveservices.speech as speechsdk
import os
import openai
# import openai.error
import requests.exceptions

# Set up the wake word and stop word
WAKE_WORD = "Hey Raspberry"
STOP_WORD = "Stop"

# Initialize command execution flag
execute_commands = False

# Set up Azure Cognitive Services Speech
speech_key = os.environ.get('cognitive_services_speech_key')
service_region, endpoint = "australiaeast", "https://australiaeast.api.cognitive.microsoft.com/sts/v1.0/issuetoken"

try:
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region)  # https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts
    speech_config.speech_synthesis_voice_name = "en-US-AshleyNeural"
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
except ValueError as ex:
    print(f"Error: {ex}")
    exit(1)

# Set up Azure Cognitive Services Speech
speech_key = os.environ.get('cognitive_services_speech_key')
service_region, endpoint = "australiaeast", "https://australiaeast.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
speech_config = speechsdk.SpeechConfig(
    subscription=speech_key, region=service_region)
# https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts
speech_config.speech_synthesis_voice_name = "en-US-AshleyNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

# Set up Azure OpenAI
openai.api_key = os.environ.get('openai_api_key')
openai.api_base = os.environ.get('openai_api_base')
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

# Define a function to generate a response using Azure OpenAI


def process_commands(text):
    if "lights" in text and "turn on" in text:
        execute_light_on_command()

    # Example command: "Play some music"
    elif "play" in text and "music" in text:
        execute_play_music_command()


def keyword_listener(event):
    global execute_commands

    if event.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        recognized_text = event.result.text
        print(f"Recognized speech: {recognized_text}")

        # Check if the wake word is detected
        if WAKE_WORD in recognized_text:
            execute_commands = True
            print("Listening...")

            # Generate a response using OpenAI API
            response = openai_generate_response(recognized_text)

            # Print the response
            print(f"OpenAI response: {response}")

            # Synthesize the response into speech
            speech_synthesizer.speak_text_async(response).get()

            # Check speech synthesis result
            if event.result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesized to speaker for text [{}]".format(
                    response))
            elif event.result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = event.result.cancellation_details
                print("Speech synthesis canceled: {}".format(
                    cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    if cancellation_details.error_details:
                        print("Error details: {}".format(
                            cancellation_details.error_details))
                print("Did you update the subscription info?")
                exit(1)

        # Check if the stop word is detected
        elif STOP_WORD in recognized_text:
            execute_commands = False
            print("Stopped listening.")

        # Process commands only if the execute_commands flag is set
        if execute_commands:
            process_commands(recognized_text)

    # Error handling
    elif event.result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(
            event.result.no_match_details))
    elif event.result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = event.result.cancellation_details
        print("Speech Recognition canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(
                cancellation_details.error_details))
        print("Did you update the subscription info?")
        exit(1)


# Connect the keyword listener to the recognized event
speech_recognizer.recognized.connect(keyword_listener)

# Start continuous speech recognition
speech_recognizer.start_continuous_recognition()
# speech_recognizer.recognize_once()

while True:
    pass
