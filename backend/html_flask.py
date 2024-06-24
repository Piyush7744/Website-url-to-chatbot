from flask import Flask, request, jsonify
from backend import run_vector_index
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Apply CORS to your Flask app

@app.route('/api/run-vector-index', methods=['POST'])
def run_vector_index_api():
    try:
        # Assume the request body contains the file path
        file_path = request.json.get('file_path')
        query = request.json.get('query')
        
        query_engine = run_vector_index(file_path)
        response = query_engine.query(query)
        
        return jsonify({'success': True, 'response': response.response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
