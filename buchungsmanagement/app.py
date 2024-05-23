from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

buchungen = []

@app.route('/buchungen', methods=['GET', 'POST'])
def manage_buchungen():
    if request.method == 'POST':
        new_buchung = request.json
        if not new_buchung or 'id' not in new_buchung:
            return jsonify({'error': 'Invalid data'}), 400
        buchungen.append(new_buchung)
        return jsonify(new_buchung), 201
    return jsonify(buchungen)

@app.route('/buchungen/<int:buchung_id>', methods=['GET', 'PUT', 'DELETE'])
def buchung_details(buchung_id):
    b = next((b for b in buchungen if b['id'] == buchung_id), None)
    if b is None:
        return jsonify({'error': 'Buchung not found'}), 404
    if request.method == 'GET':
        return jsonify(b)
    elif request.method == 'PUT':
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid data'}), 400
        b.update(data)
        return jsonify(b)
    elif request.method == 'DELETE':
        buchungen.remove(b)
        return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
