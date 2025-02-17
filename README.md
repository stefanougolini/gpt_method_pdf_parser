# PDF Methods Extractor

## Overview

This script extracts the "Methods" section from scientific papers in PDF format using OpenAI's Assistant API. It processes all PDFs in a specified folder, sends them to the Assistant for analysis, and saves the extracted methods sections to an output file.
Currently being affected by max_token response of the assistant. Methods will be truncated or summarized.

## Requirements

Ensure you have the following installed before running the script:
````
pip install -r requirements.txt
````
## Dependencies

openai (for interacting with OpenAI's API)

google-genai (for interacting with Gemini API)

python-dotenv (for managing API keys securely)

## Setup

API Key Configuration

https://ai.google.dev/gemini-api/docs/api-key (for gemini)
https://platform.openai.com/docs/quickstart (for OpenAI)

Create a .env file in the same directory as the script.

Add your OpenAI API key:
````
OPENAI_API_KEY=your_openai_api_key_here
````
## Prompt Setup

Create a prompt.txt file in the same directory.

Add the extraction prompt (e.g., "Extract the Methods section from the attached paper...").

## Usage

The script can be executed in two ways:

Option 1: Run as a Python Script
````
python gpt_method_pdf_parser.py <pdf_folder> <output_file> <assistant_id>
````

Example:
````
python gpt_method_pdf_parser.py ./pdfs methods_output.txt xyz
````

Option 2: Call the Function Programmatically

You can also import and call the process_pdf_folder function in another script:
````
from script import process_pdf_folder

pdf_folder = "./pdfs"
output_file = "methods_output.txt"
assistant_id = "xyz"

process_pdf_folder(pdf_folder, output_file, assistant_id)
````

## How It Works

Uploads PDFs: The script scans the specified folder and uploads each PDF to OpenAI's API.

Sends Query: It retrieves the extraction prompt from prompt.txt and sends a request to the Assistant.

Processes Responses: The Assistant extracts the Methods section and returns the text.

Saves Results: The extracted text is appended to the specified output file.

## Notes

Ensure that the Assistant ID is valid and has access to the necessary tools for document processing.

The script includes a timeout of 5 minutes per document to prevent excessive waiting.\

