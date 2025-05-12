from flask import Flask, render_template, request, send_file, redirect, url_for, session
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from fpdf import FPDF
import io
import os
import pyrebase

# ------------------- Firebase Config -------------------
firebase_config = {
    "apiKey": "AIzaSyCadTe-BQpf4cl9WRbeZ6-HnrBVBGSAnYM",
    "authDomain": "ailawyer-43a70.firebaseapp.com",
    "databaseURL": "https://console.firebase.google.com/project/ailawyer-43a70/firestore",
    "projectId": "ailawyer-43a70",
    "storageBucket": "ailawyer-43a70.firebasestorage.app",
    "messagingSenderId": "410384414203",
    "appId": "1:410384414203:web:7d1e09262451c6c79ec75e",
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
# ---------------------------------------------------------

# Flask App Setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'
chat_history = []

# Set your GROQ_API_KEY
os.environ["GROQ_API_KEY"] = "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"

# Initialize Groq LLM
llm = ChatGroq(
    model_name="llama3-8b-8192",
    temperature=0.3
)

# Create Prompt Template
prompt = PromptTemplate(
    input_variables=["case_description"],
    template="""You are an experienced and ethical lawyer.
Analyze the following case carefully and provide:
- Legal reasoning
- Possible legal sections involved
- Suggest next steps for the client

Case Details:
{case_description}

Respond in a professional, clear, and structured manner.
"""
)

lawyer_chain = LLMChain(llm=llm, prompt=prompt)

# ---------------- Routes ----------------

@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['idToken']
            return redirect(url_for('index'))  # Redirect to index page after login
        except Exception as e:
            message = "Login failed. Check your credentials."
    return render_template('login.html', message=message)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            session['user'] = user['idToken']
            return redirect(url_for('index'))  # Redirect to index page after signup
        except Exception as e:
            message = "Signup failed. Try again."
    return render_template('signup.html', message=message)


@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    advice = None
    if request.method == 'POST':
        case_description = request.form.get('case_description')
        if case_description:
            advice = lawyer_chain.run(case_description=case_description)
            chat_history.append({
                'case': case_description,
                'advice': advice
            })
    return render_template('index.html', advice=advice, chat_history=chat_history)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('landing'))  # Redirect to login after logout


@app.route('/download/<int:chat_id>')
def download(chat_id):
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if 0 <= chat_id < len(chat_history):
        case = chat_history[chat_id]['case']
        advice = chat_history[chat_id]['advice']

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Case Description:\n{case}\n\nAdvice:\n{advice}")

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_output = io.BytesIO(pdf_bytes)

        return send_file(
            pdf_output,
            mimetype='application/pdf',
            download_name=f"legal_advice_{chat_id}.pdf",
            as_attachment=True
        )
    return redirect(url_for('index'))

# ---------------- Main ----------------

if __name__ == '__main__':
    app.run(debug=True)
