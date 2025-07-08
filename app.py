from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import joblib
import csv
from flask import Response
import pytesseract
from PIL import Image
import os



pytesseract.pytesseract.tesseract_cmd = r'E:\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Needed for session management

# Load model (already done above)
model = joblib.load('spam_model.pkl')

# ---- UPDATED SPAM CHECK FUNCTION ----
def check_spam_confidence(text):
    prob = model.predict_proba([text])[0][1]  # probability of being spam
    prediction = "Spam" if prob >= 0.5 else "Not Spam"
    confidence = round(prob * 100, 2)
    return prediction, confidence


# ---- SAVE POST TO DATABASE ----
def insert_post(username, post, result):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (username, post, result) VALUES (?, ?, ?)", (username, post, result))
    conn.commit()
    conn.close()


# ---- HOME PAGE ----
@app.route('/')
def index():
    return render_template('index.html')

# ---- CHECK SPAM ----
@app.route('/check', methods=['POST'])
def check():
    username = request.form['username']
    post_text = request.form['post'].strip()
    image = request.files.get('image')

    def check():
        if not session.get('user_logged_in'):
            return redirect('/login_user')

    # Check if image uploaded
    if image and image.filename != '':
        image_path = os.path.join("uploads", image.filename)
        os.makedirs("uploads", exist_ok=True)
        image.save(image_path)

        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)

        post_text += " " + extracted_text.strip()

    if not post_text:
        return render_template('result.html', result="No content found in post or image.", confidence="0")

    result, confidence = check_spam_confidence(post_text)
    insert_post(username, post_text, f"{result} ({confidence}%)")
    return render_template('result.html', result=result, confidence=confidence,
                       username=username, post=post_text)

@app.route('/feedback', methods=['POST'])
def feedback():
    username = request.form['username']
    post = request.form['post']
    feedback = request.form['feedback']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET feedback = ? WHERE username = ? AND post = ?", 
                   (feedback, username, post))
    conn.commit()
    conn.close()

    return render_template('result.html', result="Thanks for your feedback!", confidence="", username="", post="")

# ---- ADMIN LOGIN ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin_user = request.form['username']
        admin_pass = request.form['password']
        if admin_user == 'admin' and admin_pass == 'admin123':
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

# ---- LOGOUT ----
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/login')

# ---- ADMIN DASHBOARD (PROTECTED) ----
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect('/login')

    search_query = request.args.get('search', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if search_query:
        cursor.execute("SELECT * FROM posts WHERE username LIKE ? OR post LIKE ?", 
                       (f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM posts WHERE result LIKE 'Spam%'")
    spam_count = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM posts WHERE result LIKE 'Not Spam%'")
    not_spam_count = cursor.fetchone()[0] or 0

    # NEW: Count feedback
    cursor.execute("SELECT COUNT(*) FROM posts WHERE feedback = 'Yes'")
    feedback_yes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM posts WHERE feedback = 'No'")
    feedback_no = cursor.fetchone()[0]

    conn.close()

    return render_template('admin.html', posts=posts,
                           spam_count=spam_count,
                           not_spam_count=not_spam_count,
                           feedback_yes=feedback_yes,
                           feedback_no=feedback_no)



@app.route('/export')
def export():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    rows = cursor.fetchall()
    conn.close()

    def generate():
        data = [['ID', 'Username', 'Post', 'Result']]
        data += rows
        output = ''
        for row in data:
            output += ','.join([str(cell).replace(',', ';') for cell in row]) + '\n'
        return output

    return Response(
        generate(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=spam_data.csv"}
    )

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect('/login_user')
        except:
            conn.close()
            return "Username already exists."
    return render_template('signup.html')

@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_logged_in'] = True
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid credentials!"
    return render_template('login_user.html')

@app.route('/logout_user')
def logout_user():
    session.pop('user_logged_in', None)
    session.pop('user', None)
    return redirect('/login_user')



# ---- RUN SERVER ----
if __name__ == '__main__':
    app.run(debug=True)
