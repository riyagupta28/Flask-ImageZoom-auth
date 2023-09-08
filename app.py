from flask import redirect, url_for
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_limiter import Limiter
import os
from flask import render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Set up JWT and limiter
jwt = JWTManager(app)
# limiter = Limiter(app, key_func=lambda: request.remote_addr)
jwt = JWTManager(app)
limiter = Limiter(app)
limiter.key_func = lambda: request.remote_addr



@app.route('/')
def login_page():
    return render_template('login.html')


@jwt_required()  # Assuming you want authentication for the upload page
def upload_page():
    return render_template('upload.html')

# Temporary storage for uploaded images (replace with your preferred storage)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Implement your user authentication logic here
# Example: Dummy user for demonstration
users = {
    'username': 'password',
}

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username not in users or users[username] != password:
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=username)
    return  render_template("upload.html")

@app.route('/upload', methods=['GET'])
@jwt_required()
def upload_page():
    token = request.args.get('token') 
    if token: 
        request.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return render_template('upload.html') 
    else:
        return jsonify({"message": "Token is missing"}), 401
    
    return render_template('upload.html')


@app.route('/zoom/<filename>') 
def display_image_with_zoom(filename): 
    return render_template('zoom.html', filename=filename)

# Route for image upload
@app.route('/upload', methods=['POST'])

@limiter.limit("5 per minute")
def upload_file():

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"})
    filename = file.filename
    #filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    return render_template("result.html",filename=filename)

if __name__ == '__main__':
    app.run(debug=True)