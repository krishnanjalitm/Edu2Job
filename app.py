import os
import sqlite3
import pickle
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "edu2job_secret_key" # session management

# 1. upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 2. database1
# def init_db():
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     cursor.execute('''CREATE TABLE IF NOT EXISTS users 
#                       (id INTEGER PRIMARY KEY AUTOINCREMENT, 
#                        username TEXT UNIQUE, 
#                        password TEXT, 
#                        resume_path TEXT)''')
#     conn.commit()
#     conn.close()

# init_db()
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # old user table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       username TEXT UNIQUE, 
                       password TEXT, 
                       resume_path TEXT,
                       prediction_result TEXT)''')
    
    # new score table
    cursor.execute('''CREATE TABLE IF NOT EXISTS scores 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       username TEXT, 
                       score INTEGER, 
                       date TEXT)''')
    conn.commit()
    conn.close()

# don't forget to call function
init_db()
# 3. load ml model
model = pickle.load(open('model.pkl', 'rb'))
le = pickle.load(open('label_encoder.pkl', 'rb'))

# --- ROUTES ---

@app.route('/login')
def home():
    return render_template('login.html')

@app.route('/')
def land():
    return render_template('land.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

# reg (Database insert + File upload)
@app.route('/register_process', methods=['POST'])
def register_process():
    username = request.form['username']
    password = request.form['password']
    resume = request.files.get('resume')
    
    resume_path = ""
    if resume and resume.filename != '':
        filename = secure_filename(resume.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(resume_path)

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, resume_path) VALUES (?, ?, ?)", 
                       (username, password, resume_path))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    except sqlite3.IntegrityError:
        return "Username already exists! <a href='/register'>Try again</a>"
#new 0
# ലോഗിൻ പ്രോസസ്സ് (Database check)
# @app.route('/login_process', methods=['POST'])
# def login_process():
#     username = request.form['username']
#     password = request.form['password']
    
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
#     user = cursor.fetchone()
#     conn.close()
    
#     if user:
#         session['user'] = username
#         return redirect(url_for('predict_form'))
#     else:
#         return "Invalid Credentials! <a href='/'>Go back</a>"

#new1
# @app.route('/login_process', methods=['POST'])
# def login_process():
#     username = request.form['username']
#     password = request.form['password']
    
#     # 1. (Hardcoded for security)
#     if username == 'admin' and password == 'admin123':
#         session['user'] = 'admin'
#         return redirect(url_for('admin_dashboard'))
    
#     # 2.  (Database)
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
#     user = cursor.fetchone()
#     conn.close()
    
#     if user:
#         session['user'] = username
#         return redirect(url_for('predict_form'))
#     else:
#         return "Invalid Credentials! <a href='/'>Go back</a>"

#new 2
@app.route('/login_process', methods=['POST'])
def login_process():
    username = request.form['username']
    password = request.form['password']
    
    if username == 'admin' and password == 'admin123':
        session['user'] = 'admin'
        return redirect(url_for('admin_dashboard'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user'] = username
        # go to dashboard
        return redirect(url_for('student_dashboard'))
    else:
        return "Invalid Credentials! <a href='/'>Go back</a>"
#student dashboard 1
# @app.route('/student_dashboard')
# def student_dashboard():
#     if 'user' in session:
#         return render_template('student_dashboard.html')
#     return redirect(url_for('home'))

#result
@app.route('/result')
def result():
    if 'user' in session:
        return render_template('result.html')
    return redirect(url_for('home'))

# prediction form for logged peopleS
@app.route('/predict_form')
def predict_form():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('home'))

# പ്രെഡിക്ഷൻ ലോജിക്
@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('home'))

    # ഫോമിൽ നിന്നുള്ള വിവരങ്ങൾ എടുക്കുന്നു
    features = [
        float(request.form['cgpa']),
        1 if request.form['python'] == 'Yes' else 0,
        1 if request.form['java'] == 'Yes' else 0,
        1 if request.form['sql'] == 'Yes' else 0,
        1 if request.form['ml'] == 'Yes' else 0,
        1 if request.form['webdev'] == 'Yes' else 0,
        int(request.form['comm']),
        1 if request.form['internship'] == 'Yes' else 0,
        int(request.form['projects']),
        int(request.form['certs'])
    ]
    
    final_features = [np.array(features)]
    prediction = model.predict(final_features)
    output = le.inverse_transform(prediction)[0]

    return render_template('result.html', prediction_text=f'Recommended Job Role: {output}')

# logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


import pdfplumber

@app.route('/predict_via_resume')
def predict_via_resume():
    if 'user' not in session:
        return redirect(url_for('home'))

    # ഡാറ്റാബേസിൽ നിന്ന് യൂസറുടെ റെസ്യൂമെ പാത്ത് എടുക്കുന്നു
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT resume_path FROM users WHERE username=?", (session['user'],))
    resume_path = cursor.fetchone()[0]
    conn.close()

    if not resume_path or not os.path.exists(resume_path):
        return "Resume not found! Please register with a resume."

    # PDF-ൽ നിന്ന് ടെക്സ്റ്റ് റീഡ് ചെയ്യുന്നു
    text = ""
    with pdfplumber.open(resume_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text().lower()

    # കീവേഡുകൾ വെച്ച് ഇൻപുട്ട് തയ്യാറാക്കുന്നു (Simple Logic)
    # മോഡലിന് 10 ഇൻപുട്ടുകൾ വേണം: [cgpa, python, java, sql, ml, webdev, comm, internship, projects, certs]
    
    # നോട്ടീസ്‌: റെസ്യൂമെയിൽ നിന്ന് CGPA എടുക്കുന്നത് പ്രയാസമായതിനാൽ ഡിഫോൾട്ട് ആയി 7.0 നൽകുന്നു
    features = [
        7.0, # Default CGPA
        1 if 'python' in text else 0,
        1 if 'java' in text else 0,
        1 if 'sql' in text else 0,
        1 if 'machine learning' in text or 'ml' in text else 0,
        1 if 'web' in text or 'flask' in text or 'html' in text else 0,
        1, # Default Medium Communication
        1 if 'internship' in text else 0,
        text.count('project'), # check how much project keyword
        text.count('certificate') # count of certificate
    ]

    final_features = [np.array(features)]
    prediction = model.predict(final_features)
    output = le.inverse_transform(prediction)[0]

    return render_template('result.html', prediction_text=f'Based on your Resume, Recommended Role: {output}')

# admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    # to check admin
    if 'user' in session and session['user'] == 'admin':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # details of each users
        cursor.execute("SELECT id, username, resume_path FROM users")
        users = cursor.fetchall()
        conn.close()
        return render_template('admin_dashboard.html', users=users)
    return "Access Denied! Only Admin can view this page."

# (Delete User)
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user' in session and session['user'] == 'admin':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    return "Unauthorized action."

# Mock Test page
@app.route('/mock_test')
def mock_test():
    if 'user' not in session: return redirect(url_for('home'))
    return render_template('mock_test.html')

# Java Mock Test 
# @app.route('/test/java')
# def java_test():
#     if 'user' not in session: return redirect(url_for('home'))
#     # questions
#     questions = [
#         {"id": 1, "q": "What is JVM?", "options": ["Java Virtual Machine", "Java Very Much", "Joint Virtual Model", "None"], "ans": "Java Virtual Machine"},
#         {"id": 2, "q": "What is JDK?", "options": ["Java Development Kit", "Java Data Kit", "Java Design Kit", "None"], "ans": "Java Development Kit"}
#     ]
#     return render_template('test_page.html', subject="Java", questions=questions)

# result
# ടെസ്റ്റ് സബ്മിറ്റ് ചെയ്യുമ്പോൾ സ്കോർ സേവ് ചെയ്യാൻ
# @app.route('/submit_test', methods=['POST'])
# def submit_test():
#     if 'user' not in session: return redirect(url_for('home'))
    
#     # ഉദാഹരണത്തിന് 10-ൽ 8 സ്കോർ കിട്ടി എന്ന് കരുതുക (ഇവിടെ നിങ്ങൾക്ക് ലോജിക് ചേർക്കാം)
#     score = 8 
    
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     # ഓരോ ടെസ്റ്റിനും പുതിയ റോ ആഡ് ചെയ്യുന്നു (ഇതിനായി ഒരു 'scores' ടേബിൾ കൂടി വേണം)
#     cursor.execute("INSERT INTO scores (username, score, date) VALUES (?, ?, date('now'))", 
#                    (session['user'], score))
#     conn.commit()
#     conn.close()
    
#     return redirect(url_for('student_dashboard'))

@app.route('/submit_test', methods=['POST'])
def submit_test():
    if 'user' not in session: return "Unauthorized", 401
    
    score = request.form.get('score') # JavaScript-ൽ നിന്ന് സ്കോർ എടുക്കുന്നു
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (username, score, date) VALUES (?, ?, date('now'))", 
                   (session['user'], int(score),))
    conn.commit()
    conn.close()
    return "OK", 200

# സ്റ്റുഡന്റ് ഡാഷ്‌ബോർഡിൽ സ്കോർ അയക്കാൻ
@app.route('/student_dashboard')
def student_dashboard():
    if 'user' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT score FROM scores WHERE username=? ORDER BY id ASC", (session['user'],))
        scores_data = [row[0] for row in cursor.fetchall()]
        conn.close()
        return render_template('student_dashboard.html', scores=scores_data)
    return redirect(url_for('home'))

# DSA Mock Test
# @app.route('/test/dsa')
# def dsa_test():
#     if 'user' not in session: return redirect(url_for('home'))
#     questions = [
#         {"id": 1, "q": "Which data structure works on LIFO principle?", "options": ["Queue", "Stack", "Array", "Linked List"], "ans": "Stack"},
#         {"id": 2, "q": "Time complexity of binary search is?", "options": ["O(n)", "O(log n)", "O(n^2)", "O(1)"], "ans": "O(log n)"},
#         # ഇവിടെ നിങ്ങൾക്ക് ബാക്കി 15 ചോദ്യങ്ങൾ വരെ ചേർക്കാം...
#     ]
#     return render_template('test_page.html', subject="Data Structures", questions=questions)


@app.route('/test/java')
def java_test():
    if 'user' not in session: return redirect(url_for('home'))
    questions = [
        {"id": 1, "q": "Which of these is not a primitive data type?", "options": ["int", "char", "String", "boolean"], "ans": "String"},
        {"id": 2, "q": "What is the size of float variable in Java?", "options": ["8 bit", "16 bit", "32 bit", "64 bit"], "ans": "32 bit"},
        {"id": 3, "q": "Which keyword is used to create a subclass in Java?", "options": ["extends", "implements", "inherits", "sub"], "ans": "extends"},
        {"id": 4, "q": "JVM stands for?", "options": ["Java Virtual Machine", "Java Variable Machine", "Joint Virtual Module", "None"], "ans": "Java Virtual Machine"},
        {"id": 5, "q": "Which of these is used to handle exceptions?", "options": ["try-catch", "if-else", "for-loop", "switch"], "ans": "try-catch"},
        {"id": 6, "q": "Default value of an integer variable in Java?", "options": ["0", "1", "null", "undefined"], "ans": "0"},
        {"id": 7, "q": "Which package contains the Scanner class?", "options": ["java.lang", "java.util", "java.io", "java.net"], "ans": "java.util"},
        {"id": 8, "q": "Can we override a static method?", "options": ["Yes", "No", "Only in same package", "Sometimes"], "ans": "No"},
        {"id": 9, "q": "Which of these is a reserved keyword?", "options": ["volatile", "main", "system", "value"], "ans": "volatile"},
        {"id": 10, "q": "Which method is the entry point of a Java program?", "options": ["start()", "main()", "init()", "run()"], "ans": "main()"},
        {"id": 11, "q": "Which memory is used for object storage?", "options": ["Stack", "Heap", "Registers", "Queue"], "ans": "Heap"},
        {"id": 12, "q": "Inheritance is used for?", "options": ["Encapsulation", "Code Reusability", "Security", "Compilation"], "ans": "Code Reusability"},
        {"id": 13, "q": "Final keyword on a class means?", "options": ["Cannot be inherited", "Cannot be instantiated", "Cannot have methods", "None"], "ans": "Cannot be inherited"},
        {"id": 14, "q": "Constructor return type is?", "options": ["void", "int", "No return type", "Object"], "ans": "No return type"},
        {"id": 15, "q": "Is Java platform independent?", "options": ["Yes", "No", "Partially", "Only on Windows"], "ans": "Yes"}
    ]
    return render_template('test_page.html', subject="Java", questions=questions)

@app.route('/test/dsa')
def dsa_test():
    if 'user' not in session: return redirect(url_for('home'))
    questions = [
        {"id": 1, "q": "LIFO stands for?", "options": ["Last In First Out", "Lead In Fast Out", "Last In Final Out", "None"], "ans": "Last In First Out"},
        {"id": 2, "q": "Which data structure uses LIFO?", "options": ["Queue", "Stack", "Array", "Linked List"], "ans": "Stack"},
        {"id": 3, "q": "Which data structure uses FIFO?", "options": ["Stack", "Queue", "Tree", "Graph"], "ans": "Queue"},
        {"id": 4, "q": "Time complexity of searching in a Hash Table (average)?", "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"], "ans": "O(1)"},
        {"id": 5, "q": "A tree with no nodes is called?", "options": ["Empty Tree", "Null Tree", "Zero Tree", "Rootless"], "ans": "Null Tree"},
        {"id": 6, "q": "Which sort has O(n log n) average complexity?", "options": ["Bubble Sort", "Merge Sort", "Selection Sort", "Insertion Sort"], "ans": "Merge Sort"},
        {"id": 7, "q": "In a linked list, each node contains?", "options": ["Data", "Link", "Data & Link", "Address"], "ans": "Data & Link"},
        {"id": 8, "q": "Binary search works on?", "options": ["Sorted Array", "Unsorted Array", "Linked List", "Graph"], "ans": "Sorted Array"},
        {"id": 9, "q": "A graph with no cycles is called?", "options": ["Tree", "Path", "Acyclic Graph", "Linear Graph"], "ans": "Acyclic Graph"},
        {"id": 10, "q": "Full form of BST?", "options": ["Binary Search Tree", "Binary Selection Tool", "Basic Search Tree", "None"], "ans": "Binary Search Tree"},
        {"id": 11, "q": "Which is a linear data structure?", "options": ["Tree", "Graph", "Array", "BST"], "ans": "Array"},
        {"id": 12, "q": "Postfix expression for A+B?", "options": ["+AB", "AB+", "A+B", "BA+"], "ans": "AB+"},
        {"id": 13, "q": "Adding element to a stack is?", "options": ["Pop", "Push", "Enqueue", "Dequeue"], "ans": "Push"},
        {"id": 14, "q": "The height of a root node is?", "options": ["0", "1", "Height of tree", "-1"], "ans": "0"},
        {"id": 15, "q": "BFS uses which data structure?", "options": ["Stack", "Queue", "Tree", "Array"], "ans": "Queue"}
    ]
    return render_template('test_page.html', subject="Data Structures", questions=questions)

if __name__ == "__main__":
    app.run(debug=True)