from flask import Flask, request, render_template, send_from_directory, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialize Flask App
app = Flask(__name__, template_folder="templates")

# Ensure 'static/uploads' directory exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database Configuration (Using Clever Cloud Environment Variables)
DB_USER = os.getenv("MYSQL_ADDON_USER")
DB_PASS = os.getenv("MYSQL_ADDON_PASSWORD")
DB_HOST = os.getenv("MYSQL_ADDON_HOST")
DB_NAME = os.getenv("MYSQL_ADDON_DB")
DB_PORT = "3306"  # Default MySQL Port for Clever Cloud

# Ensure all database environment variables exist
if not all([DB_USER, DB_PASS, DB_HOST, DB_NAME]):
    raise ValueError("Missing database environment variables! Check your configuration.")

# Set up database URI
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database and Migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define Database Models
class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thought = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    ip = db.Column(db.String(45), nullable=False)

class IPAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False)

# Home Page
@app.route("/")
def index():
    return render_template("index.html")

# Handle Thought Submission
@app.route("/submit", methods=["POST"])
def submit():
    try:
        thought = request.form.get("thought")
        file = request.files.get("image")
        ip = request.remote_addr  # Get User IP

        image_path = None
        if file:
            image_filename = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(image_filename)
            image_path = os.path.join("static", "uploads", file.filename)  # Relative path

        # Insert into database
        new_thought = Thought(thought=thought, image=image_path, ip=ip)
        db.session.add(new_thought)
        db.session.commit()

        return jsonify({"message": "Submitted Successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Handle IP Capture
@app.route("/capture-ip", methods=["POST"])
def capture_ip():
    try:
        ip = request.json.get("ip")
        new_ip = IPAddress(ip=ip)
        db.session.add(new_ip)
        db.session.commit()
        return jsonify({"message": "IP Captured"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Download Meme Template (ZIP File)
@app.route("/download-templates")
def download_templates():
    return send_file("static/meme_templates.zip", as_attachment=True)

# Serve Uploaded Images
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
