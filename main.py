from flask import Flask, request, jsonify, abort, render_template
from flask_httpauth import HTTPTokenAuth
import jwt, os, time, bgQA, CreateVectorDb as cdb

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

SECRET_KEY = 'secret-key'  # Ideally, this should be in a config file or environment variable
EXPIRATION_TIME = 3600  # 1 hour


def get_folder_names():
    root_directory = os.getcwd()
    subfolder = "games"
    folder_path = os.path.join(root_directory, subfolder)
    
    folder_names = []
    for entry in os.scandir(folder_path):
        if entry.is_dir():
            folder_names.append(entry.name)
    return folder_names

@auth.verify_token
def verify_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return False
    if 'username' in data:
        return data['username']
    return False

@app.route('/api/token')
def get_token():
    username = request.args.get('username')
    password = request.args.get('password')
    if username == 'admin' and password == 'password':  # In real application, you should check this in your database
        token = jwt.encode({'username': username, 'exp': time.time() + EXPIRATION_TIME}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token, 'duration': EXPIRATION_TIME})
    return abort(401)

@app.route('/api/chat', methods=['POST'])
@auth.login_required
def chat():    
    game = request.json.get('game', '') 
    prompt = request.json.get('prompt', '')
    b=bgQA.DocQA(game)
    b = b.chat_with_user(prompt)
    print(jsonify({'response': b["response"]}))
    return jsonify({'response': b["response"]})

@app.route('/')
def main():
    db = cdb.VectorDB('Wingspan')
    col_list = db.get_collections()
    col_formatted = []
    for col in col_list:
        col = col.replace("-", " ")
        col_formatted.append(col)
    return render_template('index.html', games=col_formatted)

if __name__ == '__main__':
    app.run(debug=True)