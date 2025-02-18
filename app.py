from flask import Flask, request, render_template, send_from_directory, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Ensure 'static/uploads' directory exists
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Configuration (Using Clever Cloud Environment Variables)
DB_USER = os.getenv("DB_USER")  # Your Clever Cloud database username
DB_PASS = os.getenv("DB_PASSWORD")  # Your Clever Cloud database password
DB_HOST = os.getenv("DB_HOST")  # Your Clever Cloud database host
DB_NAME = os.getenv("DB_NAME")  # Your Clever Cloud database name

if not all([DB_USER, DB_PASS, DB_HOST, DB_NAME]):
    raise ValueError("Missing required database environment variables!")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db = SQLAlchemy(app)

# Define Database Models
class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thought = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    ip = db.Column(db.String(45), nullable=False)

class IPAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False)

# Create tables if they don’t exist
with app.app_context():
    db.create_all()

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Handle Thought Submission
@app.route('/submit', methods=['POST'])
def submit():
    try:
        thought = request.form.get('thought')
        file = request.files.get('image')
        ip = request.remote_addr  # Get User IP

        # Save image if uploaded
        image_path = None
        if file:
            image_filename = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(image_filename)
            image_path = image_filename  # Save path for database

        # Insert into database
        new_thought = Thought(thought=thought, image=image_path, ip=ip)
        db.session.add(new_thought)
        db.session.commit()

        return jsonify({"message": "Submitted Successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Handle IP Capture
@app.route('/capture-ip', methods=['POST'])
def capture_ip():
    try:
        ip = request.json.get('ip')
        new_ip = IPAddress(ip=ip)
        db.session.add(new_ip)
        db.session.commit()
        return jsonify({"message": "IP Captured"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Download Meme Template (Multiple Templates in ZIP)
@app.route('/download-templates')
def download_templates():
    return send_file("static/meme_templates.zip", as_attachment=True)

# Serve Uploaded Images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Run Flask
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
