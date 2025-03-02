from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.oauth2 import service_account
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel
from fpdf import FPDF
import os

# Configuration variables
project_id = "ocr-reader-452416"
location = "us"  # Format is "us" or "eu"
file_path = "/Users/sadie/Documents/hackathon/SampleContract-Shuttle.pdf" ##/Users/sadie/Desktop/Spain/ImpresoRellenarDescargar.pdf
credentials_path = "/Users/sadie/Documents/hackathon/ocr-reader-452416-1e75aaed777e.json"
processor_display_name = "ORC-Reader"  # Changed from "OCR-Reader" to "ORC-Reader"

# Initialize credentials once
credentials = service_account.Credentials.from_service_account_file(credentials_path)
# Initialize Vertex AI with explicit credentials
vertexai.init(project=project_id, location="us-east1", credentials=credentials)

def create_pdf_from_response(ai_response, original_text=None, output_path="ai_response.pdf"):
    """
    Create a PDF file with the AI response and optionally the original text.
    Uses standard fonts with fallback for special characters.
    
    Args:
        ai_response (str): The AI-generated response text
        original_text (str, optional): The original extracted text from the document
        output_path (str): Path where the PDF should be saved
    
    Returns:
        str: Path to the created PDF file
    """
    # Function to sanitize text for basic FPDF
    def sanitize_text(text):
        if text is None:
            return ""
        # Replace problematic characters
        text = text.replace('€', 'EUR')
        text = text.replace('á', 'a')
        text = text.replace('é', 'e')
        text = text.replace('í', 'i')
        text = text.replace('ó', 'o')
        text = text.replace('ú', 'u')
        text = text.replace('ñ', 'n')
        text = text.replace('ü', 'u')
        text = text.replace('Á', 'A')
        text = text.replace('É', 'E')
        text = text.replace('Í', 'I')
        text = text.replace('Ó', 'O')
        text = text.replace('Ú', 'U')
        text = text.replace('Ñ', 'N')
        text = text.replace('Ü', 'U')
        
        # Strip any other non-Latin1 characters
        return ''.join(c if ord(c) < 256 else '_' for c in text)
    
    # Initialize PDF object
    pdf = FPDF()
    pdf.add_page()
    
    # Set font for title (using built-in fonts)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AI Document Analysis", ln=True, align="C")
    pdf.ln(10)
    
    # # Add original text if provided
    # if original_text:
    #     pdf.set_font("Arial", "B", 12)
    #     pdf.cell(0, 10, "Original Document Text:", ln=True)
    #     pdf.set_font("Arial", "", 10)
        
    #     # Sanitize and handle multi-line text
    #     sanitized_text = sanitize_text(original_text)
    #     lines = sanitized_text.split('\n')
    #     for line in lines:
    #         pdf.multi_cell(0, 5, line)
    #     pdf.ln(10)
    
    # Add AI response
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "AI Explanation of Legal Terms:", ln=True)
    pdf.set_font("Arial", "", 10)
    
    # Sanitize and handle multi-line text for AI response
    sanitized_response = sanitize_text(ai_response)
    response_lines = sanitized_response.split('\n')
    for line in response_lines:
        pdf.multi_cell(0, 5, line)
    
    # Save the PDF
    pdf.output(output_path)
    print(f"PDF created successfully at: {os.path.abspath(output_path)}")
    return os.path.abspath(output_path)

def get_gemini_response(prompt_text, file_path):
    # Read the text file content
    with open(file_path, "r") as file:
        file_content = file.read()
    
    # Initialize the Gemini model (credentials now passed through vertexai initialization)
    model = GenerativeModel("gemini-1.5-pro")
    
    # Create a combined prompt with your text and the file content
    combined_prompt = f"{prompt_text}\n\nHere is the text file content:\n{file_content}"
    
    # Generate content
    response = model.generate_content(combined_prompt)
    
    # Return the response as a string
    return response.text

def find_processor_by_display_name(
    project_id: str,
    location: str,
    display_name: str
):

    """Find a processor by its display name and return its ID."""
    # Set up client with explicit credentials
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts, credentials=credentials)
    
    # Get the location path
    parent = client.common_location_path(project_id, location)
    
    # List all processors
    processors = client.list_processors(parent=parent)
    
    # Find processor by display name (case-insensitive)
    target_processor = None
    print("Available processors:")
    for processor in processors:
        processor_id = processor.name.split('/')[-1]
        print(f"ID: {processor_id}, Name: {processor.display_name}, Type: {processor.type_}")
        
        # Case-insensitive comparison
        if processor.display_name.lower() == display_name.lower():
            target_processor = processor
    
    if target_processor:
        processor_id = target_processor.name.split('/')[-1]
        print(f"\nFound processor: {target_processor.display_name} (ID: {processor_id})")
        return processor_id
    else:
        print(f"\nNo processor found with name: {display_name}")
        return None

def process_document(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    generate_pdf: bool = True,
    pdf_output_path: str = "document_analysis.pdf"
):
    """Process a document using an existing processor and optionally create a PDF with the analysis."""
    # Set up client with explicit credentials (use the global credentials)
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts, credentials=credentials)
    
    # Get the full processor name
    processor_name = client.processor_path(project_id, location, processor_id)
    
    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()
    
    # Load binary data
    raw_document = documentai.RawDocument(
        content=image_content,
        mime_type="application/pdf",
    )
    
    # Configure the process request
    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=raw_document
    )
    
    # Process the document
    result = client.process_document(request=request)
    document = result.document
    
    # Save extracted text to file
    try:
        with open("file_contents.txt", "x") as file:
            file.write(document.text)
            file.close()
    except FileExistsError:
        with open("file_contents.txt", "w") as file:
            file.write(document.text)
            file.close()
    
    # Print the results
    print("The document contains the following text:")
    print(document.text)
    
    # Get AI explanation
    ai_response = get_gemini_response(
        "Can you explain some of the confusing legal terms in this file? Respond in the language of the file", 
        file_path)
    print("\n=== AI Analysis of Legal Terms ===")
    print(ai_response)
    
    # Generate PDF if requested
    if generate_pdf:
        pdf_path = create_pdf_from_response(
            ai_response=ai_response,
            original_text=document.text,
            output_path=pdf_output_path
        )
        return document, ai_response, pdf_path
    
    return document, ai_response

if __name__ == "__main__":
    # Define output PDF path
    pdf_output_path = "legal_document_analysis.pdf"
    
    # Find the processor by display name
    processor_id = find_processor_by_display_name(
        project_id=project_id,
        location=location,
        display_name=processor_display_name
    )
    
    if processor_id:
        # Process the document with the found processor and generate PDF
        result = process_document(
            project_id=project_id,
            location=location,
            processor_id=processor_id,
            file_path=file_path,
            generate_pdf=True,
            pdf_output_path=pdf_output_path
        )
        
        # Unpack the result if needed
        if isinstance(result, tuple) and len(result) == 3:
            document, ai_response, pdf_path = result
            print(f"\nAnalysis PDF created at: {pdf_path}")
    else:
        # Try with the Form-parser as a fallback
        print("Trying with the Form-parser instead...")
        processor_id = find_processor_by_display_name(
            project_id=project_id,
            location=location,
            display_name="Form-parser"
        )
        
        if processor_id:
            result = process_document(
                project_id=project_id,
                location=location,
                processor_id=processor_id,
                file_path=file_path,
                generate_pdf=True,
                pdf_output_path=pdf_output_path
            )
            
            # Unpack the result if needed
            if isinstance(result, tuple) and len(result) == 3:
                document, ai_response, pdf_path = result
                print(f"\nAnalysis PDF created at: {pdf_path}")
        else:
            print("Cannot process document without a valid processor.")