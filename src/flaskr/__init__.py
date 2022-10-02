from flask import Flask, jsonify
from flask_cors import CORS

def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    @app.route('/')
    def base():
        return jsonify({
            "msg": "my API is up",
            "data": None
        })

    return app
