from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.oauth2 import service_account
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel
from fpdf import FPDF
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration variables
project_id = "ocr-reader-452416"
location = "us"  # Format is "us" or "eu"
credentials_path = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS", 
    "/Users/sadie/Documents/hackathon/ocr-reader-452416-1e75aaed777e.json"
)
processor_display_name = "OCR-Reader"

# Initialize credentials once
try:
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    # Initialize Vertex AI with explicit credentials
    vertexai.init(project=project_id, location="us-east1", credentials=credentials)
    logger.info("Credentials initialized successfully")
except Exception as e:
    logger.error(f"Error initializing credentials: {str(e)}")
    credentials = None

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
    
    try:
        # Initialize PDF object
        pdf = FPDF()
        pdf.add_page()
        
        # Set font for title (using built-in fonts)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "AI Document Analysis", ln=True, align="C")
        pdf.ln(10)
        
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
        logger.info(f"PDF created successfully at: {os.path.abspath(output_path)}")
        return os.path.abspath(output_path)
    except Exception as e:
        logger.error(f"Error creating PDF: {str(e)}")
        raise

def get_gemini_response(prompt_text, file_path):
    try:
        # Read the text file content
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # Initialize the Gemini model (credentials now passed through vertexai initialization)
        model = GenerativeModel("gemini-1.5-pro")
        
        # Create a combined prompt with your text and the file content
        combined_prompt = f"{prompt_text}\n\nHere is the text file content:\n{file_content}"
        
        # Generate content
        logger.info("Requesting AI response from Gemini")
        response = model.generate_content(combined_prompt)
        
        # Return the response as a string
        return response.text
    except Exception as e:
        logger.error(f"Error getting Gemini response: {str(e)}")
        raise

# def translate_with_vertex(text, target_language):
#     """
#     Translate text using Vertex AI Gemini model
    
#     Args:
#         text (str): The text to translate
#         target_language (str): The target language code (e.g., 'es', 'fr')
    
#     Returns:
#         str: The translated text
#     """
#     try:
#         # Map language codes to names
#         language_names = {
#             'en': 'English',
#             'es': 'Spanish',
#             'fr': 'French',
#             'de': 'German',
#             'zh': 'Chinese',
#             'ja': 'Japanese',
#             'ru': 'Russian',
#             'pt': 'Portuguese',
#             'it': 'Italian',
#             'ar': 'Arabic',
#             'hi': 'Hindi'
#         }
        
#         language_name = language_names.get(target_language, target_language)
        
#         # Initialize the Gemini model
#         model = GenerativeModel("gemini-1.5-pro")
        
#         # Special case for English translation which needs more explicit instructions
#         if target_language == 'en':
#             prompt = f"""
#             You are a professional legal translator specializing in Spanish to English translation.
            
#             Translate the following Spanish legal text into English:
            
#             {text}
            
#             Important instructions:
#             1. This is a SPANISH to ENGLISH translation task
#             2. Translate the entire text completely and accurately
#             3. Maintain all formatting, including bold text, headings, and structure
#             4. Translate all legal terms with their proper English equivalents
#             5. Do not add any explanations or notes - only provide the translation
#             """
#         else:
#             # For other languages, use the regular prompt
#             prompt = f"""
#             Translate the following text to {language_name}:
            
#             {text}
#             """
        
#         logger.info(f"Requesting translation to {language_name} using Vertex AI")
#         response = model.generate_content(prompt)
        
#         # Return the translated text
#         return response.text
#     except Exception as e:
#         logger.error(f"Error translating with Vertex AI: {str(e)}")
#         with open("translation_error.log", "w", encoding="utf-8") as f:
#             f.write(f"Error: {str(e)}\n\nText that failed to translate:\n{text}")
#         raise
def translate_with_vertex(text, target_language, use_cache=True):
    """
    Optimized translation function with caching and simplified prompts
    
    Args:
        text (str): The text to translate
        target_language (str): The target language code (e.g., 'es', 'fr')
        use_cache (bool): Whether to use translation cache
    
    Returns:
        str: The translated text
    """
    # Implement a simple in-memory cache to reduce redundant API calls
    if not hasattr(translate_with_vertex, '_translation_cache'):
        translate_with_vertex._translation_cache = {}
    
    # Check cache first
    if use_cache:
        cache_key = (text, target_language)
        if cache_key in translate_with_vertex._translation_cache:
            logger.info("Using cached translation")
            return translate_with_vertex._translation_cache[cache_key]
    
    # Simplified language mapping
    language_names = {
        'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 
        'zh': 'Chinese', 'ja': 'Japanese', 'ru': 'Russian', 
        'pt': 'Portuguese', 'it': 'Italian', 'ar': 'Arabic', 'hi': 'Hindi'
    }
    
    try:
        # Simplified prompt structure
        model = GenerativeModel("gemini-pro")  # Consider using a lighter model
        
        prompt = f"Translate the following text to {language_names.get(target_language, target_language)}:\n\n{text}"
        
        logger.info(f"Requesting translation to {target_language}")
        
        # Add timeout and error handling
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(model.generate_content, prompt)
            try:
                response = future.result(timeout=30)  # 30-second timeout
                translated_text = response.text
                
                # Cache the translation
                if use_cache:
                    translate_with_vertex._translation_cache[cache_key] = translated_text
                
                return translated_text
            
            except concurrent.futures.TimeoutError:
                logger.error("Translation timed out")
                raise TimeoutError("Translation request took too long")
    
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        # Fallback error handling
        with open("translation_error.log", "a", encoding="utf-8") as f:
            f.write(f"Translation Error: {str(e)}\n")
            f.write(f"Original Text: {text}\n")
            f.write(f"Target Language: {target_language}\n\n")
        raise
    
def clear_translation_cache():
    """Clear the in-memory translation cache."""
    if hasattr(translate_with_vertex, '_translation_cache'):
        translate_with_vertex._translation_cache.clear()
        logger.info("Translation cache cleared")

def find_processor_by_display_name(
    project_id: str,
    location: str,
    display_name: str
):
    """Find a processor by its display name and return its ID."""
    try:
        # Set up client with explicit credentials
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts, credentials=credentials)
        
        # Get the location path
        parent = client.common_location_path(project_id, location)
        
        # List all processors
        processors = client.list_processors(parent=parent)
        
        # Find processor by display name (case-insensitive)
        target_processor = None
        logger.info("Available processors:")
        for processor in processors:
            processor_id = processor.name.split('/')[-1]
            logger.info(f"ID: {processor_id}, Name: {processor.display_name}, Type: {processor.type_}")
            
            # Case-insensitive comparison
            if processor.display_name.lower() == display_name.lower():
                target_processor = processor
        
        if target_processor:
            processor_id = target_processor.name.split('/')[-1]
            logger.info(f"Found processor: {target_processor.display_name} (ID: {processor_id})")
            return processor_id
        else:
            logger.warning(f"No processor found with name: {display_name}")
            return None
    except Exception as e:
        logger.error(f"Error finding processor: {str(e)}")
        raise

def process_document(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    generate_pdf: bool = True,
    pdf_output_path: str = "document_analysis.pdf"
):
    """Process a document using an existing processor and optionally create a PDF with the analysis."""
    try:
        # Set up client with explicit credentials
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
        logger.info(f"Processing document with processor ID: {processor_id}")
        result = client.process_document(request=request)
        document = result.document
        
        # Save extracted text to file
        text_file_path = "file_contents.txt"
        try:
            with open(text_file_path, "w", encoding="utf-8") as file:
                file.write(document.text)
        except Exception as e:
            logger.error(f"Error saving text file: {str(e)}")
        
        # Get AI explanation
        prompt = "Can you explain some of the confusing legal terms in this file? Respond in the language of the file"
        logger.info(f"Getting AI explanation with prompt: {prompt}")
        ai_response = get_gemini_response(prompt, text_file_path)
        
        # Generate PDF if requested
        if generate_pdf:
            logger.info(f"Generating PDF at: {pdf_output_path}")
            pdf_path = create_pdf_from_response(
                ai_response=ai_response,
                original_text=document.text,
                output_path=pdf_output_path
            )
            return document, ai_response, pdf_path
        
        return document, ai_response, None
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise