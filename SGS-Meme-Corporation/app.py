from flask import Flask, request, render_template, send_from_directory, send_file, jsonify
import mysql.connector
import os

app = Flask(__name__)

# Ensure 'static/uploads' directory exists
UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Connect to MySQL using environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = db.cursor()
    print("✅ Database connection successful!")
except mysql.connector.Error as err:
    print(f"❌ Database connection failed: {err}")

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
    cursor.execute("INSERT INTO thoughts (thought, image, ip) VALUES (%s, %s, %s)", 
                   (thought, image_path, ip))
    db.commit()

    return jsonify({"message": "Submitted Successfully!"})

# Handle IP Capture
@app.route('/capture-ip', methods=['POST'])
def capture_ip():
    ip = request.json.get('ip')
    cursor.execute("INSERT INTO ip_addresses (ip) VALUES (%s)", (ip,))
    db.commit()
    return jsonify({"message": "IP Captured"}), 200

# Download Meme Template (Multiple Templates in ZIP)
@app.route('/download-templates')
def download_templates():
    return send_file("static/meme_templates.zip", as_attachment=True)

# Serve Uploaded Images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
