from flask import Flask, request, jsonify, render_template_string
import requests
import os
import time
import datetime
import random

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'logs.txt'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to log messages
def log_message(message):
    with open(LOG_FILE, 'a') as log:
        log.write(f"{datetime.datetime.now()} - {message}\n")

# Function to check if token is valid
def is_token_valid(access_token):
    url = f"https://graph.facebook.com/me?access_token={access_token}"
    response = requests.get(url)
    return response.status_code == 200

# Function to post a comment on Facebook
def post_comment(post_id, comment, access_token):
    url = f"https://graph.facebook.com/{post_id}/comments"
    payload = {"message": comment, "access_token": access_token}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.post(url, data=payload, headers=headers)
    
    try:
        result = response.json()
        if "error" in result:
            log_message(f"Error: {result['error']['message']}")
        return result
    except Exception as e:
        log_message(f"Error parsing response: {str(e)}")
        return {"error": "Invalid response"}

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 ArYan.x3 Comment Tool</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600&display=swap');
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Orbitron', sans-serif;
        }
        body {
            background: url('https://i.ibb.co/Fk3jDDh1/e1eb5fbc674e213aa360897ba03d2284.gif') no-repeat center center/cover;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }
        .container {
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0px 0px 30px rgba(0, 255, 255, 0.8);
            text-align: center;
            width: 90%;
            max-width: 550px;
            border: 2px solid rgba(0, 255, 255, 0.5);
            animation: neon-flicker 1.5s infinite alternate;
        }
        @keyframes neon-flicker {
            0% { box-shadow: 0px 0px 15px rgba(0, 255, 255, 0.5); }
            100% { box-shadow: 0px 0px 40px rgba(0, 255, 255, 1); }
        }
        h2 {
            color: #0ff;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 15px;
            text-transform: uppercase;
            text-shadow: 0px 0px 15px #0ff;
        }
        input, button, label {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            text-align: center;
        }
        input {
            background: rgba(0, 255, 255, 0.2);
            color: #0ff;
        }
        button {
            background: linear-gradient(90deg, #0ff, #00f);
            color: white;
            font-weight: bold;
            cursor: pointer;
            text-transform: uppercase;
        }
        button:hover {
            background: linear-gradient(90deg, #00f, #0ff);
            transform: scale(1.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🚀 ArYan Comment Tool</h2>
        <form action="/submit" method="POST" enctype="multipart/form-data">
            <input type="text" name="wall_post_id" placeholder="📌 Facebook Post ID" required>
            <input type="text" name="resume_post_id" placeholder="🔄 Resume Post ID (Optional)">
            <input type="text" name="hater_name" placeholder="😡 Enter Hater Name (Optional)">
            <label>📂 Upload Token File  <input type="file" name="token_file" required></label>
            <label>📂 Upload Comments File  <input type="file" name="comments_file" required></label>
            <label>⏱ Minimum Speed (Seconds): <input type="number" name="min_speed" min="1" value="5" required></label>
            <label>⏱ Maximum Speed (Seconds): <input type="number" name="max_speed" min="1" value="10" required></label>
            <button type="submit">🚀 Start Commenting</button>
        </form>
    </div>
</body>
</html>
    """)

@app.route('/submit', methods=['POST'])
def submit():
    wall_post_id = request.form.get('wall_post_id')
    resume_post_id = request.form.get('resume_post_id')
    hater_name = request.form.get('hater_name', '')
    min_speed = int(request.form.get('min_speed'))
    max_speed = int(request.form.get('max_speed'))
    
    token_file = request.files.get('token_file')
    comments_file = request.files.get('comments_file')

    if not token_file or not comments_file:
        return "Both token file and comments file are required!", 400

    # Save and read token file
    token_path = os.path.join(app.config['UPLOAD_FOLDER'], token_file.filename)
    token_file.save(token_path)

    with open(token_path, 'r') as f:
        tokens = [line.strip() for line in f.readlines() if line.strip()]

    if not tokens:
        return "Token file is empty!", 400

    # Save and read comments file
    comments_path = os.path.join(app.config['UPLOAD_FOLDER'], comments_file.filename)
    comments_file.save(comments_path)

    with open(comments_path, 'r') as f:
        comments = [line.strip() for line in f.readlines() if line.strip()]

    if not comments:
        return "Comments file is empty!", 400

    # Start Posting Comments
    results = []
    token_index = 0

    while True:
        for comment in comments:
            if hater_name:
                comment = f"{hater_name} {comment}"

            current_token = tokens[token_index]

            if not is_token_valid(current_token):
                token_index = (token_index + 1) % len(tokens)
                continue

            response = post_comment(wall_post_id, comment, current_token)
            results.append(response)

            sleep_time = random.randint(min_speed, max_speed)
            time.sleep(sleep_time)

        token_index = 0

    return jsonify({"message": "Comments posted successfully!", "results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
