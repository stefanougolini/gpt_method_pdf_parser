import os
import time
import pathlib
import sys
from dotenv import load_dotenv
from google import genai

# Load API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini client
client = genai.Client(api_key=API_KEY)

def upload_pdf(pdf_path):
    """Uploads a PDF and returns its file reference."""
    file_path = pathlib.Path(pdf_path)
    uploaded_file = client.files.upload(file=file_path)
    print(f"File uploaded: {pdf_path} (Name: {uploaded_file.name})")
    return uploaded_file

def get_prompt():
    """Reads the prompt from prompt.txt."""
    with open("prompt.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

def ask_methods_section(uploaded_file, pdf_filename, output_file):
    """Sends a request to extract the Methods section from a PDF."""
    prompt = get_prompt()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[uploaded_file, prompt]
    )
    extracted_text = response.text
    print(extracted_text)

    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"\n---\n📄 **File:** {pdf_filename}\n")
        f.write(extracted_text)

    return extracted_text

def process_pdf_folder(pdf_folder, output_file):
    """Processes all PDFs in the given folder."""
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDFs found in the folder!")
        return

    print(f"Found {len(pdf_files)} PDFs. Processing...")
    for pdf_filename in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_filename)
        uploaded_file = upload_pdf(pdf_path)
        ask_methods_section(uploaded_file, pdf_filename, output_file)

    print(f"\n✅ Extraction complete! All methods saved in '{output_file}'.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <pdf_folder> <output_file>")
        sys.exit(1)

    pdf_folder = sys.argv[1]
    output_file = sys.argv[2]
    process_pdf_folder(pdf_folder, output_file)
