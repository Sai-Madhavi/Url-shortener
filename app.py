from flask import Flask, request, redirect, render_template_string
import sqlite3
import random
import string
import webbrowser
import threading
from urllib.parse import urlparse

app = Flask(__name__)
DB_NAME = "url_shortener.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''CREATE TABLE IF NOT EXISTS urls
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     original_url TEXT NOT NULL,
                     short_code TEXT UNIQUE NOT NULL)''')
    conn.commit()
    conn.close()

def get_short_code():
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(6))
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM urls WHERE short_code = ?", (code,))
        if cursor.fetchone() is None:
            conn.close()
            return code
        conn.close()

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>URL Shortener</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
        input { width: 70%; padding: 10px; margin: 10px 0; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #d4edda; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🔗 URL Shortener</h1>
    <form method="POST" action="/shorten">
        <input type="url" name="url" placeholder="Paste URL here (https://example.com)" required>
        <button type="submit">Shorten URL</button>
    </form>
    {% if short_url %}
    <div class="result">
        <h3>Your Short URL:</h3>
        <a href="{{ short_url }}">{{ short_url }}</a>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form.get('url', '').strip()
    if not original_url.startswith('http'):
        original_url = 'https://' + original_url
    
    short_code = get_short_code()
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)", (original_url, short_code))
    conn.commit()
    conn.close()
    
    short_url = f"http://127.0.0.1:5000/r/{short_code}"
    return render_template_string(HOME_HTML, short_url=short_url)

@app.route('/r/<short_code>')
def redirect_url(short_code):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return redirect(result[0])
    return "<h1>URL not found</h1>", 404

def open_browser():
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    init_db()
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True, host='127.0.0.1', port=5000)