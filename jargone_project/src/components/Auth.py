from flask import Flask, jsonify, request, send_from_directory
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os  
from flask_cors import CORS

app = Flask(__name__, static_folder="./dist", static_url_path="")
CORS(app, origins=["http://localhost:5173"])
auth = HTTPBasicAuth()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    username = db.Column(db.String(), unique=True, nullable=False) 
    password_hash = db.Column(db.String(), nullable=False)


    def set_password(self, password):  # Changed to use self instead of user
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):  # Changed to use self
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.create_all()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return username

# API routes
@app.route("/api/protected")
@auth.login_required
def protected():
    return jsonify({"message": f"Welcome {auth.current_user()}!"})

@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()  # Fixed: add parentheses to call the method
        username = data.get("username")  # Fixed: use data instead of request.json
        password = data.get("password")

        if not username or not password:  # Added 'not' before password
            return jsonify({"error": "Must enter username and password"}), 400
        
        if User.query.filter_by(username=username).first():  # Fixed: use = not ==
            return jsonify({"error": "User already exists, log in!"}), 400  # Added status code
        
        new_user = User(username=username)
        new_user.set_password(password)  # This will use the instance method
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "User registered successfully"}), 200
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])  # Added login route
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Must provide username and password"}), 400
        
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({"message": "Login successful", "token": "sample-token"}), 200
    
    return jsonify({"error": "Invalid username or password"}), 401

@app.route("/api/users", methods=["GET"])
@auth.login_required  
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username} for user in users])

# Catch-all route for React frontend - must be at the end
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)  # Added debug=True for development