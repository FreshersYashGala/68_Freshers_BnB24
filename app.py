from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
import pandas as pd
from docx import Document
import os
import PyPDF2

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///MEvaluee.db"
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)


class evaluee(db.Model):
    rank =db.Column(db.Integer,primary_key = True)
    name =db.Column(db.String(200),nullable = False)
    match =db.Column(db.Integer)
    experience =db.Column(db.Integer)
    gap =db.Column(db.Integer)
    date_Created =db.Column(db.DateTime,default=datetime.utcnow)
    def __repr__(self) -> str:
        return f"{self.rank} - {self.name}"

@app.route('/')
def hello_world():
    return render_template('frmTalentEvaluation.html')
    #return 'Hello, World!'

def create_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ""
    df =  pd.read_csv('C:/68_Freshers_BnB24/68_Freshers_BnB24/Engineer.csv')
    total_words = 0
    found_occurrences = 0
    for column in df.columns:
        for keyword in df[column].dropna():
            if pd.notna(keyword):
                words = str(keyword).split()
                total_words += len(words)
            for paragraph in doc.paragraphs:
                if keyword in paragraph.text:
                    found_occurrences += 1
                    print(f"Found '{keyword}' in paragraph: '{paragraph.text}'")

    if found_occurrences == 0:
        print(f"Keyword '{keyword}' not found in the DOCX file.")

    print(found_occurrences)
    return text

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        df =  pd.read_csv('C:/68_Freshers_BnB24/68_Freshers_BnB24/Engineer.csv')

    found_occurrences = 0
    for column in df.columns:
        for keyword in df[column].dropna():
            if pd.notna(keyword):
                words = str(keyword).split()
                total_words += len(words)
            for page_number in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_number)
                if keyword in page.extractText():
                    print(f"Found '{keyword}' in paragraph: '{page.extract_text()}'")

        if found_occurrences == 0:
            print(f"Keyword '{keyword}' not found in the DOCX file.")

    print(found_occurrences)
        
    return found_occurrences

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    create_upload_folder()

    if 'txtResumes' not in request.files:
        return 'No file part'

    file = request.files['txtResumes']

    if file.filename == '':
        return 'No selected file'

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        if filename.lower().endswith('.docx'):
            extracted_text = extract_text_from_docx(filename)
        elif filename.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(filename)
        else:
            return 'Unsupported file format'

        return render_template('frmUploadResult.html', filename=file.filename, extracted_text=extracted_text)

    return 'Invalid file format'

if __name__ == "__main__":
    app.run(debug=True)





















if __name__ == "__main__":
    app.run(debug=True, port = 8000)