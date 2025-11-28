from flask import Flask, jsonify, render_template
import json
import os

app = Flask(__name__)
STATS_FILE = '/home/mokhtar/sdn_project/stats.json'

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    if not os.path.exists(STATS_FILE):
        return jsonify({})
    try:
        with open(STATS_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # Run on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
