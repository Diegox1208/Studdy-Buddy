from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS - allow all origins temporarily for debugging
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Create uploads directory
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Store file metadata in memory (for testing)
files_db = []

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_FOLDER / safe_filename
    
    file.save(file_path)
    
    # Store metadata
    file_info = {
        'file_id': len(files_db) + 1,
        'filename': file.filename,
        'saved_as': safe_filename,
        'file_path': str(file_path),
        'size': os.path.getsize(file_path),
        'uploaded_at': datetime.now().isoformat(),
        'type': file.content_type
    }
    files_db.append(file_info)
    
    print(f"✅ File saved: {file_path}")
    print(f"📊 Total files: {len(files_db)}")
    
    return jsonify(file_info), 200

@app.route('/api/files', methods=['GET'])
def list_files():
    """List all uploaded files"""
    return jsonify(files_db), 200

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file"""
    global files_db
    file_info = next((f for f in files_db if f['file_id'] == file_id), None)
    
    if not file_info:
        return jsonify({'error': 'File not found'}), 404
    
    # Delete physical file
    file_path = Path(file_info['file_path'])
    if file_path.exists():
        file_path.unlink()
    
    # Remove from database
    files_db = [f for f in files_db if f['file_id'] != file_id]
    
    print(f"🗑️ File deleted: {file_info['filename']}")
    
    return jsonify({'message': 'File deleted'}), 200

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'running',
        'upload_folder': str(UPLOAD_FOLDER),
        'total_files': len(files_db)
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print("🚀 Starting Study Buddy Backend...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"📤 Upload endpoint: http://localhost:{port}/api/upload")
    print(f"🔧 Debug mode: {debug}")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
