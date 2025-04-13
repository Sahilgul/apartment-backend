# run.py
from app import create_app, db
from app.models.user import User
from app.models.listing import Listing, Amenity, ListingImage
from app.models.review import Review
from flask import jsonify, request
from flask_cors import CORS

app = create_app()

# Only use this (remove any manual after_request CORS handling)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
        }
    },
)

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Apartment Listing App!'})

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Listing': Listing,
        'Amenity': Amenity,
        'ListingImage': ListingImage,
        'Review': Review
    }


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"status": "preflight"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin"))
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)