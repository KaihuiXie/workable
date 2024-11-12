import logging
from flask import Flask, jsonify
from routers.users import users_bp

app = Flask(__name__)

app.register_blueprint(users_bp)


@app.route("/healthcheck", methods=["GET"])
def health_check():
    try:
        return jsonify({"status": "ok"})
    except Exception as e:
        logging.error(f"Health Check Failed: {e}")
        return jsonify({"detail": "Service unavailable"}), 500
    
if __name__ == '__main__':
   app.run(port=8080)