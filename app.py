import os
import json
import base64
import requests
import argparse
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from datetime import datetime
import re

# Load environment variables
load_dotenv()

# Get API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scans-page')
def scans_page():
    return render_template('scans.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'photo' not in request.files:
            return jsonify({'success': False, 'error': 'No image file uploaded'}), 400
            
        image = request.files['photo']
        if not image:
            return jsonify({'success': False, 'error': 'No image file uploaded'}), 400
        
        # Read image data
        image_data = image.read()
        
        # Convert image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.2-11b-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is the name of this album and who is the singer/artist? Please respond in this exact format: Album: [album name] Artist: [singer/artist name]. If you cannot clearly read or identify either the album name or artist name, respond with 'Album: unclear Artist: unclear'. Do not make up or guess names if you cannot read them clearly."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }
        
        # Make request to Groq API
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            # Check if the API couldn't identify the album or artist
            if "unclear" in analysis.lower():
                return jsonify({
                    'success': False,
                    'info': "I couldn't read the album or artist name clearly. Please try scanning again with better lighting or a clearer image."
                })
            
            # Only save to history if we have a clear result with both album and artist
            if "Album:" in analysis and "Artist:" in analysis and "unclear" not in analysis.lower():
                save_success = save_to_history(analysis)
                return jsonify({
                    'success': True, 
                    'info': analysis,
                    'saved': save_success
                })
            else:
                return jsonify({
                    'success': False,
                    'info': "I couldn't read the album or artist name clearly. Please try scanning again with better lighting or a clearer image."
                })
        else:
            return jsonify({'success': False, 'error': f"API request failed: {response.text}"}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def save_to_history(analysis):
    try:
        history_file = 'data/history.json'
        os.makedirs('data', exist_ok=True)
        
        history = []
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        
        # Extract album and artist from the analysis
        album_match = re.search(r'Album: (.*?)(?=Artist:|$)', analysis)
        artist_match = re.search(r'Artist: (.*?)$', analysis)
        
        album = album_match.group(1).strip() if album_match else "Unknown Album"
        artist = artist_match.group(1).strip() if artist_match else "Unknown Artist"
        
        # Create a scan record with timestamp
        scan_record = {
            'album': album,
            'artist': artist,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to history
        history.append(scan_record)
        
        # Save to file
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
        # Also save to a public JSON file that can be accessed from anywhere
        public_history_file = 'static/scans.json'
        with open(public_history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error saving to history: {str(e)}")
        return False

@app.route('/scans')
def get_scans():
    """Endpoint to get all successful scans"""
    try:
        # Try to get from the public JSON file first
        public_history_file = 'static/scans.json'
        if os.path.exists(public_history_file):
            with open(public_history_file, 'r') as f:
                return jsonify(json.load(f))
        
        # Fall back to the data directory file
        history_file = 'data/history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return jsonify(json.load(f))
        
        return jsonify([])
    except Exception as e:
        print(f"Error getting scans: {str(e)}")
        return jsonify([])

@app.route('/records')
def get_records():
    try:
        history_file = 'data/history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return jsonify(json.load(f))
        return jsonify([])
    except Exception:
        return jsonify([])

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Vinyl Record Scanner')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5000)), help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    args = parser.parse_args()
    
    # Get IP address for display
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    
    print(f"Starting server on http://{ip}:{args.port}")
    print(f"You can access this from other devices on your network using: http://{ip}:{args.port}")
    print("Press Ctrl+C to stop the server")
    
    app.run(host=args.host, port=args.port) 