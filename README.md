# Speech-to-Text and Text-to-Speech using Azure Cognitive Services and OpenAI

This Python script demonstrates how to use Azure Cognitive Services Speech and OpenAI to perform speech-to-text and text-to-speech operations.

## Prerequisites

- Python 3.x
- Azure Cognitive Services Speech subscription key and region
- Azure OpenAI API key and API endpoint base URL

> Note: Follow my post [here](https://graef.io/posts/building-your-own-gpt-powered-ai-voice-assistant-with-azure-cognitive-services-and-openai/) for a detailed guide on how to set up Azure Cognitive Services and OpenAI.

## Installation

1. Clone the repository to your local machine.
2. Install the required Python packages using pip: `pip install -r requirements.txt`.
3. Set the environment variables for the Azure Cognitive Services Speech subscription key and region, and the OpenAI API key and API base URL.
   1. export cognitive_services_speech_key=<KEY_VALUE>
   2. export openai_api_key=<KEY_VALUE>
   3. export openai_api_base=https://<VALUE>.openai.azure.com

## Usage

1. Run the `start.py` script using Python: `python start.py`.
2. Speak into the microphone when prompted.
3. The script will recognize your speech and generate a response using OpenAI.
4. The response will be synthesized into speech and played through the speakers.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
