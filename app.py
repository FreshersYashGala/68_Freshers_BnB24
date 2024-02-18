
from warnings import catch_warnings
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy 
import pandas as pd
from docx import Document
import os
from datetime import datetime
import PyPDF2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///MEvaluee.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class MEvaluee(db.Model):
    Srno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(200), nullable=False)
    Match = db.Column(db.Integer)
    Experience = db.Column(db.Integer)
    Gap = db.Column(db.Integer)
    Date_created= db.Column(db.DateTime, default=datetime.utcnow)
    Rank = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"{self.rank} - {self.name}"

def create_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)

        # Your existing code for text extraction from DOCX

    except FileNotFoundError:
        print(f"Error: File not found at {docx_path}")
        return "File not found"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error during document processing"
    
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
    return found_occurrences/total_words*100

def extract_text_from_pdf(pdf_path):
    total_words = 0  # Initialize total_words
    found_occurrences = 0
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        df = pd.read_csv('C:/68_Freshers_BnB24/68_Freshers_BnB24/Engineer.csv')

    for column in df.columns:
        for keyword in df[column].dropna():
            if pd.notna(keyword):
                words = str(keyword).split()
                total_words += len(words)
            for page_number in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_number)
                if keyword in page.extractText():
                    print(f"Found '{keyword}' in paragraph: '{page.extractText()}'")
                    found_occurrences += 1

    if found_occurrences == 0:
        print(f"Keyword '{keyword}' not found in the PDF file.")

    print(found_occurrences)
    return found_occurrences/total_words*100

@app.route('/')
def index():
    return render_template('frmTalentEvaluation.html')  # Corrected template name

@app.route('/upload', methods=['POST'])
def upload_file():
    create_upload_folder()

    if 'txtResumes' not in request.files:
        return 'No file part'

    file = request.files['txtResumes']

    if file.filename == '':
        return 'No selected file'

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        if file_path.lower().endswith('.docx'):
            Match = extract_text_from_docx(file_path)
        elif file_path.lower().endswith('.pdf'):
            Match = extract_text_from_pdf(file_path)
        else:
            return 'Unsupported file format'
        
        Name = request.form['txtName']
    
        mevaluee = MEvaluee( Name=Name,Match=Match)
        db.session.add(mevaluee)
        db.session.commit ()
        allMEvaluee = MEvaluee.query.all()

        return render_template('frmTalentEvaluation.html',allMEvaluee=allMEvaluee)

    return 'Invalid file format'

@app.route('/reset', methods=['POST'])
def Clear_Table():
    with app.app_context():
        # Drop all tables
        db.drop_all()

        # Recreate all tables
        db.create_all()

        # Additional setup (if needed)
        # For example, create some default records
        default_record = MEvaluee(Name="Default Name")
        db.session.add(default_record)
        db.session.commit()

    return render_template('frmTalentEvaluation.html')


    

with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True, port=8000)