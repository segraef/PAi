import azure.cognitiveservices.speech as speechsdk
import sys
import os
import openai
import openai.error
import requests.exceptions

# Set up the wake word and stop word
WAKE_WORD = "Hey Azure"
STOP_WORD = "Stop."
EXIT_WORD = "Exit"

# Initialize command execution flag
execute_commands = False

# Set up Azure OpenAI
openai.api_key = os.environ.get('openai_api_key')
openai.api_base = os.environ.get('openai_api_base')
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

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

# Function to generate a response using Azure OpenAI


def openai_generate_response(prompt):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        return response.choices[0].text.strip()
    except openai.error.InvalidRequestError as e:
        print(f"Invalid request error: {e}")
    except openai.error.AuthenticationError as e:
        print(f"Authentication error: {e}")
    except openai.error.APIConnectionError as e:
        print(f"API connection error: {e}")
    except openai.error.OpenAIError as e:
        print(f"OpenAI error: {e}")


def process_commands(text):
    if "lights" in text and "turn on" in text:
        execute_light_on_command()

    # Example command: "Play some music"
    elif "play" in text and "music" in text:
        execute_play_music_command()


def keyword_listener(event):
    global execute_commands
    # speech_recognizer.recognize_once()
    if event.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        recognized_text = event.result.text
        print(f"Recognized speech: {recognized_text}")

        # Check if the wake word is detected
        if WAKE_WORD in recognized_text:
            execute_commands = True
            print("Yes, I'm listening ...")

            # speech_recognizer.start_continuous_recognition()
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
            print("Stopped speaking.")

            # Interrupt the speech synthesis if it is still in progress
            speech_synthesizer.stop_speaking()

        # Check if the exit word is detected
        elif EXIT_WORD in recognized_text:
            execute_commands = False
            print("Goodbye.")
            exit(0)

            # Stop the speech recognizer
            # speech_recognizer.stop_continuous_recognition()

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


    # Connect the keyword listener to the speech recognizer
speech_recognizer.recognized.connect(keyword_listener)
print("Connected keyword listener to speech recognizer")

# Start the speech recognition
print("Starting speech recognition")
speech_recognizer.start_continuous_recognition()
print("Speech recognition started")

while True:
    pass
