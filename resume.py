import re
import mysql.connector
from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
import base64

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'resumes_database'

mysql = MySQL(app)

def extract_text_from_resume(resume_text):
    # Simulated function to extract text from the uploaded resume file
    return resume_text

def preprocess_text(text):
    # Code to preprocess the extracted text
    # For simplicity, we'll just convert text to lowercase and remove non-alphanumeric characters
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def screen_resume(resume_text, qualifications):
    # Code to screen the resume based on qualifications
    matched_qualifications = [qualification for qualification in qualifications if qualification in resume_text]
    return bool(matched_qualifications), matched_qualifications

def fetch_resume_texts_from_database():
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    cursor = connection.cursor()

    # Fetch resume texts from the database
    cursor.execute("SELECT file_content FROM resumes")
    resume_texts = cursor.fetchall()

    # Close the database connection
    connection.close()
    
    return resume_texts

@app.route('/')
def home():
    return render_template('upload_form.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'message': 'No file selected for uploading'}), 400

    try:
        # Read the file content
        resume_content = file.read()

        # Convert content to base64 for storage
        resume_base64 = base64.b64encode(resume_content).decode('utf-8')

        # Save the file to the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO resumes (file_name, file_type, file_content) VALUES (%s, %s, %s)",
                       (file.filename, file.content_type, resume_base64))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'Resume uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/screen_resumes')
def screen_resumes():
    # Sample qualifications relevant to the job
    qualifications = ["python", "machine learning", "data analysis", "communication skills", "teamwork"]

    # Fetch resume texts from the MySQL database
    resume_texts = fetch_resume_texts_from_database()

    # Counters for total number of resumes and qualified resumes
    total_resumes = len(resume_texts)
    qualified_resumes_count = 0

    for resume_text_tuple in resume_texts:
        resume_text = resume_text_tuple[0]  # Extracting text from tuple
        # Preprocess the extracted text
        preprocessed_text = preprocess_text(resume_text)

        # Screen the resume based on qualifications
        qualified, _ = screen_resume(preprocessed_text, qualifications)

        if qualified:
            qualified_resumes_count += 1
            print("Resume meets the qualifications.")
        else:
            print("Resume does not meet the qualifications.")

    return jsonify({
        'total_resumes': total_resumes,
        'qualified_resumes_count': qualified_resumes_count
    })

if __name__ == '__main__':
    app.run(debug=True)
