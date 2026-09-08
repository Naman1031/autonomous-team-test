import os
from flask import Flask, request, jsonify
from models.user import User

app = Flask(__name__)

@app.route('/user', methods=['GET'])
def get_user(user_token):
    if 'Authorization' not in request.headers:
        return jsonify({'error': 'Missing authorization token'}), 401

    token = request.headers['Authorization'].split(' ')[1]

    user = User.get_by_token(token)

    if user is None:
        return jsonify({'error': 'Invalid token'}), 403

    return jsonify(user.to_dict()), 200

if __name__ == '__main__':
    app.run(debug=True)