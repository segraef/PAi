import azure.cognitiveservices.speech as speechsdk
import os
import openai

# Set up Azure Cognitive Services Speech
speech_key = os.environ.get('cognitive_services_speech_key')
service_region, endpoint = "australiaeast", "https://australiaeast.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = "en-US-AshleyNeural" # https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

# Set up Azure OpenAI
openai.api_key = os.environ.get('openai_api_key')
openai.api_base = os.environ.get('openai_api_base')
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

# Define a function to generate a response using Azure OpenAI
def openai_generate_response(prompt):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.5,
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

print("Say something...")

# Recognize speech from an audio input stream
result_stt = speech_recognizer.recognize_once()

# Check speech recognition result
if result_stt.reason == speechsdk.ResultReason.RecognizedSpeech:
    recognized_text = result_stt.text
    print("Recognized: {}".format(recognized_text))
elif result_stt.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result_stt.no_match_details))
elif result_stt.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result_stt.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))

# Generate response using Azure OpenAI
response_text = openai_generate_response(recognized_text)
print("Generated response:", response_text)

# Synthesize the response into speech
result_tts = speech_synthesizer.speak_text_async(response_text).get()

# Check speech synthesis result
if result_tts.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized to speaker for text [{}]".format(response_text))
elif result_tts.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result_tts.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
    print("Did you update the subscription info?")
