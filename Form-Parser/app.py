from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import logging
import vertexai
from vertexai.generative_models import GenerativeModel
# Import document processing functions
from document_processor import find_processor_by_display_name, process_document, translate_with_vertex

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Simple welcome route
@app.route('/')
def index():
    return jsonify({"message": "Welcome to JarGone API!"})

# Upload and process file
@app.route('/upload', methods=['POST'])
def upload_file():
    # Get target language if provided (default to English)
    target_language = request.form.get('language', 'en')
    logger.info(f"Processing document with target language: {target_language}")
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info(f"File saved to {filepath}")
        
        # Process with AI
        try:
            # Find the processor
            processor_id = find_processor_by_display_name(
                project_id="ocr-reader-452416",
                location="us",
                display_name="OCR-Reader"
            )
            
            if not processor_id:
                # Try alternate name if primary name doesn't work
                processor_id = find_processor_by_display_name(
                    project_id="ocr-reader-452416",
                    location="us",
                    display_name="ORC-Reader"
                )
                
            if processor_id:
                # Process the document
                result_filename = f"analyzed_{filename}"
                result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
                
                document, ai_response, pdf_path = process_document(
                    project_id="ocr-reader-452416",
                    location="us",
                    processor_id=processor_id,
                    file_path=filepath,
                    generate_pdf=True,
                    pdf_output_path=result_path
                )
                
                # Translate the document text and analysis
                translated_document = None
                translated_analysis = None
                is_translated = False
                
                try:
                    logger.info(f"Translating document text to {target_language}")
                    
                    # Translate the document content itself
                    translated_document = translate_with_vertex(
                        text=document.text,
                        target_language=target_language
                    )
                    
                    # Also translate the analysis if available
                    if ai_response:
                        translated_analysis = translate_with_vertex(
                            text=ai_response,
                            target_language=target_language
                        )
                    
                    is_translated = True
                    
                    # Create a new PDF with the translated content
                    from fpdf import FPDF
                    
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(0, 10, "Translated Document Content", ln=True, align="C")
                    pdf.ln(10)
                    
                    # Add the translated document content
                    pdf.set_font("Arial", "", 10)
                    
                    # Handle multi-line text for document content
                    doc_lines = translated_document.split('\n')
                    for line in doc_lines:
                        # Sanitize text for PDF
                        line = ''.join(c if ord(c) < 256 else '_' for c in line)
                        pdf.multi_cell(0, 5, line)
                    
                    # Add the analysis if available
                    if translated_analysis:
                        pdf.add_page()
                        pdf.set_font("Arial", "B", 16)
                        pdf.cell(0, 10, "AI Analysis of Legal Terms", ln=True, align="C")
                        pdf.ln(5)
                        
                        pdf.set_font("Arial", "", 10)
                        analysis_lines = translated_analysis.split('\n')
                        for line in analysis_lines:
                            # Sanitize text for PDF
                            line = ''.join(c if ord(c) < 256 else '_' for c in line)
                            pdf.multi_cell(0, 5, line)
                    
                    # Save the translated PDF
                    translated_filename = f"translated_{filename}"
                    translated_path = os.path.join(app.config['UPLOAD_FOLDER'], translated_filename)
                    pdf.output(translated_path)
                    
                    # Update the result filename
                    result_filename = translated_filename
                    logger.info(f"Translated PDF saved to {translated_path}")
                except Exception as e:
                    error_msg = f"Translation error: {str(e)}"
                    logger.error(error_msg)
                    # Continue with untranslated version rather than failing
                
                return jsonify({
                    "message": "File processed successfully",
                    "original_text": document.text,
                    "ai_analysis": ai_response,
                    "translated_document": translated_document,
                    "translated_analysis": translated_analysis,
                    "is_translated": is_translated,
                    "target_language": target_language,
                    "result_file": result_filename
                }), 200
            else:
                logger.error("No valid processor found")
                return jsonify({"error": "No valid processor found"}), 500
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Processing error: {error_msg}")
            return jsonify({"error": error_msg}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

# Download processed file
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)