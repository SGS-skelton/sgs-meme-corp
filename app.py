from flask import Flask, request, render_template, send_from_directory, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Ensure 'static/uploads' directory exists
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Configuration
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")  # Change for Railway
DB_PORT = os.getenv("DB_PORT", "3306")  # Default MySQL Port
DB_NAME = os.getenv("DB_NAME", "sgs_meme_corporation")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db = SQLAlchemy(app)

# Define Thought Model
class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thought = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    ip = db.Column(db.String(45), nullable=False)

class IPAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False)

with app.app_context():
    db.create_all()  # Ensure tables exist

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Handle Thought Submission
@app.route('/submit', methods=['POST'])
def submit():
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

    return jsonify({"message": "Submitted Successfully!"})

# Handle IP Capture
@app.route('/capture-ip', methods=['POST'])
def capture_ip():
    ip = request.json.get('ip')
    new_ip = IPAddress(ip=ip)
    db.session.add(new_ip)
    db.session.commit()
    return jsonify({"message": "IP Captured"}), 200

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
