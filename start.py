import os
import azure.cognitiveservices.speech as speechsdk
import openai

wake_word = "Hey, Azure."
stop_word = "Stop."

# Set up Azure OpenAI
openai.api_key = os.environ.get('openai_api_key')
openai.api_base = os.environ.get('openai_api_base')
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

# Azure OpenAI deployment ID
deployment_id = 'davinci'

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

# Should be the locale for the speaker's language.
speech_config.speech_recognition_language = "en-US"
speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config)
speech_config.speech_synthesis_voice_name = 'en-US-AshleyNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config)

# Prompts Azure OpenAI with a request and synthesizes the response.


def ask_openai(prompt):

    # Ask Azure OpenAI
    response = openai.Completion.create(
        engine=deployment_id, prompt=prompt, max_tokens=100)
    text = response['choices'][0]['text'].replace(
        '\n', ' ').replace(' .', '.').strip()
    print('Azure: ' + text)

    # Azure text to speech output
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    # Check result
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized to speaker for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(
                cancellation_details.error_details))

# Continuously listens for speech input to recognize and send as text to Azure OpenAI


def chat_with_open_ai():
    while True:
        print("Listening ...")
        try:
            # Get audio from the microphone and then send it to the TTS service.
            speech_recognition_result = speech_recognizer.recognize_once_async().get()

            # If speech is recognized, send it to Azure OpenAI and listen for the response.
            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                if speech_recognition_result.text == stop_word:
                    print("Conversation ended.")
                    break
                print("Recognized speech: {}".format(
                    speech_recognition_result.text))
                ask_openai(speech_recognition_result.text)
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized: {}".format(
                    speech_recognition_result.no_match_details))
                break
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                print("Speech Recognition canceled: {}".format(
                    cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(
                        cancellation_details.error_details))
        except EOFError:
            break

# Main


try:
    chat_with_open_ai()
except Exception as err:
    print("Encountered exception. {}".format(err))
