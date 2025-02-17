import os
import time
import openai
import sys
from dotenv import load_dotenv

# Load API Key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def upload_pdf(pdf_path):
    """Uploads a PDF and returns its file ID."""
    with open(pdf_path, "rb") as file:
        uploaded_file = client.files.create(file=file, purpose="assistants")
    print(f"File uploaded: {pdf_path} (ID: {uploaded_file.id})")
    return uploaded_file.id


def get_prompt():
    """Reads the prompt from prompt.txt."""
    with open("prompt.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


def ask_methods_section(pdf_file_id, pdf_filename, assistant_id, output_file):
    """Sends a request to extract the Methods section from a PDF."""
    thread = client.beta.threads.create()
    attachments = [{"file_id": pdf_file_id, "tools": [{"type": "file_search"}]}]

    prompt = get_prompt()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
        attachments=attachments
    )
    print(f"Message sent for: {pdf_filename} (Thread ID: {thread.id})")

    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
    start_time = time.time()

    while True:
        time.sleep(10)
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        elapsed_time = time.time() - start_time
        print(f"Waiting for response... ({elapsed_time:.0f}s elapsed)")
        if elapsed_time > 300:
            print(f"Timeout reached for {pdf_filename}, skipping...")
            return None

    responses = client.beta.threads.messages.list(thread_id=thread.id)
    extracted_text = "".join(str(msg.content) for msg in responses.data)
    print(extracted_text)

    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"\n---\n📄 **File:** {pdf_filename}\n")
        f.write(extracted_text)

    return extracted_text


def process_pdf_folder(pdf_folder, output_file, assistant_id):
    """Processes all PDFs in the given folder."""
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDFs found in the folder!")
        return

    print(f"Found {len(pdf_files)} PDFs. Processing...")
    for pdf_filename in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_filename)
        pdf_file_id = upload_pdf(pdf_path)
        ask_methods_section(pdf_file_id, pdf_filename, assistant_id, output_file)

    print(f"\n✅ Extraction complete! All methods saved in '{output_file}'.")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python script.py <pdf_folder> <output_file> <assistant_id>")
        sys.exit(1)

    pdf_folder = sys.argv[1]
    output_file = sys.argv[2]
    assistant_id = sys.argv[3]

    process_pdf_folder(pdf_folder, output_file, assistant_id)
