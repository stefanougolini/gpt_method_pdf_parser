import os
import pathlib
import csv
from dotenv import load_dotenv
from google import genai

# Load API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini client
client = genai.Client(api_key=API_KEY)

# Global variable to track last used subheading
last_methods_subheading = None


def upload_pdf(pdf_path):
    """Uploads a PDF and returns its file reference."""
    file_path = pathlib.Path(pdf_path)
    uploaded_file = client.files.upload(file=file_path)
    print(f"File uploaded: {pdf_path} (Name: {uploaded_file.name})")
    return uploaded_file


def get_prompt(file_name):
    """Reads the prompt from the given file."""
    with open(file_name, "r", encoding="utf-8") as f:
        return f.read().strip()


def modify_prompt2(methods_subheading):
    """Modifies prompt2.txt to include the last methods_subheading in place of %start_paragraph."""
    global last_methods_subheading
    last_methods_subheading = methods_subheading  # Store for later restoration

    prompt2_path = "prompt2.txt"

    # Read the existing content
    with open(prompt2_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    # Replace the %start_paragraph marker with the extracted subheading
    modified_text = prompt_text.replace("%start_paragraph", methods_subheading)

    # Write the modified prompt back
    with open(prompt2_path, "w", encoding="utf-8") as f:
        f.write(modified_text)

    print(f"Updated 'prompt2.txt' with methods_subheading: {methods_subheading}")


def restore_prompt2():
    """Restores prompt2.txt by replacing the last used methods_subheading with %start_paragraph."""
    global last_methods_subheading
    if not last_methods_subheading:
        return  # No modification was made, so no need to restore

    prompt2_path = "prompt2.txt"

    with open(prompt2_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    # Replace the last used subheading back to %start_paragraph
    restored_text = prompt_text.replace(last_methods_subheading, "%start_paragraph")

    with open(prompt2_path, "w", encoding="utf-8") as f:
        f.write(restored_text)

    print("🔄 Restored 'prompt2.txt' to its original state.")
    last_methods_subheading = None  # Reset for next use


def ask_methods_section(uploaded_file, pdf_filename, output_file, prompt_file):
    """Sends a request to extract the Methods section from a PDF."""
    prompt = get_prompt(prompt_file)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[uploaded_file, prompt]
    )
    extracted_text = response.text.strip()

    # Save the response to the output file
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(extracted_text + "\n")

    # Directly check if the last characters are '1"'
    if not extracted_text.rstrip().endswith('"1"'):
        print(f"❗ Incomplete extraction for {pdf_filename}, retrying with modified prompt2.txt...")

        # Extract last methods_subheading
        last_methods_subheading = extract_last_methods_subheading(extracted_text)
        modify_prompt2(last_methods_subheading)

        # Retry with modified prompt2.txt
        result = ask_methods_section(uploaded_file, pdf_filename, output_file, "prompt2.txt")

        # Restore prompt2.txt after query submission
        restore_prompt2()

        return result

    print(f"✅ Successfully extracted methods from {pdf_filename}. Moving to next PDF.")
    return extracted_text


def extract_last_methods_subheading(response_text):
    """Extracts the last 'methods_subheading' from the response text."""
    rows = list(csv.reader(response_text.split("\n"), quotechar='"'))
    for row in reversed(rows):
        if len(row) > 4 and row[4].strip():  # Assuming 'methods_subheading' is at index 4
            return row[4].strip()
    return "Unknown"  # Fallback if nothing is found


def process_pdf_folder(pdf_folder, output_file):
    """Processes all PDFs in the given folder."""
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDFs found in the folder!")
        return

    print(f"Found {len(pdf_files)} PDFs. Processing...")

    for pdf_filename in pdf_files[:5]:  # Limit processing to first 5 PDFs
        pdf_path = os.path.join(pdf_folder, pdf_filename)
        uploaded_file = upload_pdf(pdf_path)

        # Always start fresh with prompt.txt for each new PDF
        ask_methods_section(uploaded_file, pdf_filename, output_file, "prompt.txt")

    print(f"\n✅ Extraction complete! All methods saved in '{output_file}'.")


if __name__ == "__main__":
    pdf_folder = r".\\run\\"  # Folder containing PDFs
    output_file = r"methods_extracted_v5.txt"  # Output file for extracted data
    process_pdf_folder(pdf_folder, output_file)
