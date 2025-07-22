from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # allow all origins, all routes

@app.route('/archive', methods=['POST'])
def archive():
    data = request.json
    url = data.get('url')
    print(f"Received URL to archive: {url}")
    return jsonify({'message': 'URL received', 'url': url})

if __name__ == '__main__':
    app.run(debug=True)