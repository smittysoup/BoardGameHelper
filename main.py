from flask import Flask, request, jsonify, abort, render_template
from flask_httpauth import HTTPTokenAuth
import jwt, os, time

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
    message1 = request.json.get('message1', '')
    message2 = request.json.get('message2', '')
    return jsonify({"result": message1 + ' ' + message2})

@app.route('/')
def main():
    return render_template('index.html', strings=get_folder_names())

if __name__ == '__main__':
    app.run(debug=True)