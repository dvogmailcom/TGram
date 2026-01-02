from flask import Flask, send_file, redirect, request
import sqlite3
from datetime import datetime
import io

app = Flask(__name__)

DB = "stats.db"

# Прозрачный 1x1 GIF
PIXEL = io.BytesIO(bytes.fromhex('47494638396101000100800000ffffff0000002c00000000010001000002024c01003b'))

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS opens (uid TEXT PRIMARY KEY, ts TEXT, ip TEXT, ua TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS clicks (uid TEXT, type TEXT, ts TEXT, ip TEXT, ua TEXT)''')

init_db()

@app.route('/open/<uid>.png')
def open_track(uid):
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    ts = datetime.now().isoformat()
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT OR REPLACE INTO opens VALUES (?, ?, ?, ?)", (uid, ts, ip, ua))
    PIXEL.seek(0)
    return send_file(PIXEL, mimetype='image/gif')

@app.route('/channel')
def channel():
    uid = request.args.get('uid', 'unknown')
    track_click(uid, 'channel')
    return redirect("https://t.me/dnevnilspekulanta")  # Замени!

@app.route('/contact')
def contact():
    uid = request.args.get('uid', 'unknown')
    track_click(uid, 'contact')
    return redirect("https://t.me/voroncov1249")  # Замени!

def track_click(uid, ctype):
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    ts = datetime.now().isoformat()
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT INTO clicks VALUES (?, ?, ?, ?, ?)", (uid, ctype, ts, ip, ua))

@app.route('/')
def stats():
    with sqlite3.connect(DB) as conn:
        opens = conn.execute("SELECT COUNT(*) FROM opens").fetchone()[0]
        channel = conn.execute("SELECT COUNT(*) FROM clicks WHERE type='channel'").fetchone()[0]
        contact = conn.execute("SELECT COUNT(*) FROM clicks WHERE type='contact'").fetchone()[0]
    return f"""
    <h1>📊 Статистика рассылки</h1>
    <p><strong>Открыто писем:</strong> {opens}</p>
    <p><strong>Перешли в канал:</strong> {channel}</p>
    <p><strong>Написали нам:</strong> {contact}</p>
    <p><a href="/">Обновить</a></p>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
