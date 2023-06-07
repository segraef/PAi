import azure.cognitiveservices.speech as speechsdk
import os,openai

openai.api_key = os.environ.get('openai_api_key')
openai.api_base = os.environ.get('openai_api_base')
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

speech_key = os.environ.get('cognitive_services_speech_key')
service_region, endpoint = "australiaeast", "https://australiaeast.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Set the voice name, refer to https://aka.ms/speech/voices/neural for full list.
speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

## Creates a speech synthesizer (output) and recognizer (input) using the default system audio.
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

print("Say something...")

result_stt = speech_recognizer.recognize_once()
#result_continous = speech_recognizer.start_continuous_recognition()

## Checks result.
if result_stt.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(result_stt.text))
elif result_stt.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result_stt.no_match_details))
elif result_stt.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result_stt.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))

# Azure OpenAI

def openai_generate_response(input_text):
    response = openai.Completion.create(
        engine="davinci",
        prompt=input_text,
        max_tokens=100
    )
    return response.choices[0].text.strip()

recognized_text = result_stt.text
response_text = openai_generate_response(recognized_text)
print("Generated response:", response_text)

# Synthesizes the received text to speech.
# The synthesized speech is expected to be heard on the speaker with this line executed.
result_tts = speech_synthesizer.speak_text_async(response_text).get()

# Checks result.
if result_tts.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized to speaker for text [{}]".format(response_text))
elif result_tts.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result_tts.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
    print("Did you update the subscription info?")
