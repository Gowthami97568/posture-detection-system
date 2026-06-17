from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global posture data
data = {
    "current_bad": 0,
    "total_bad": 0
}

# API to GET posture data (used by React)
@app.route('/posture')
def get_posture():
    return jsonify(data)

# API to UPDATE posture data (used by Python script)
@app.route('/update/<int:current>/<int:total>')
def update_posture(current, total):
    data["current_bad"] = current
    data["total_bad"] = total
    return jsonify({"status": "updated"})

# Root route (optional but useful)
@app.route('/')
def home():
    return "Posture API Running ✅"

if __name__ == "__main__":
    app.run(debug=True)