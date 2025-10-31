from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
from utils.pdf_parser import parse_pdfs_and_generate_timetable
from utils.timetable_builder import generate_pdf

app = Flask(__name__)
CORS(app)

# Configuration
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({"message": "Personalized Timetable Generator API", "status": "running"})

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Check if files are present
        if 'faculty' not in request.files or 'formb' not in request.files:
            return jsonify({"error": "Both faculty timetable and form B files are required"}), 400
        
        faculty_file = request.files['faculty']
        formb_file = request.files['formb']
        
        # Check if files are selected
        if faculty_file.filename == '' or formb_file.filename == '':
            return jsonify({"error": "No files selected"}), 400
        
        if not (allowed_file(faculty_file.filename) and allowed_file(formb_file.filename)):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Save files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as faculty_temp:
            faculty_file.save(faculty_temp.name)
            faculty_path = faculty_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as formb_temp:
            formb_file.save(formb_temp.name)
            formb_path = formb_temp.name
        
        try:
            # Process the PDFs
            timetable_data = parse_pdfs_and_generate_timetable(faculty_path, formb_path)
            
            # Clean up temp files
            os.unlink(faculty_path)
            os.unlink(formb_path)
            
            return jsonify(timetable_data)
            
        except Exception as e:
            # Clean up temp files in case of error
            if os.path.exists(faculty_path):
                os.unlink(faculty_path)
            if os.path.exists(formb_path):
                os.unlink(formb_path)
            return jsonify({"error": f"Error processing PDFs: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/timetable', methods=['GET'])
def view_timetable():
    # This would typically get data from session or database
    # For MVP, we'll return a template that can be populated via JS
    return render_template('timetable.html')

@app.route('/download', methods=['POST'])
def download_timetable():
    try:
        timetable_data = request.json
        if not timetable_data:
            return jsonify({"error": "No timetable data provided"}), 400
        
        # Generate PDF
        pdf_path = generate_pdf(timetable_data)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name='personalized_timetable.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"error": f"Error generating PDF: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)