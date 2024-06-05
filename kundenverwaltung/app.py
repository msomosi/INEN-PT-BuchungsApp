from flask import Flask, request, jsonify

app = Flask(__name__)

kunden = []

@app.route('/kunden', methods=['GET', 'POST'])
def manage_kunden():
    if request.method == 'POST':
        new_kunde = request.json
        kunden.append(new_kunde)
        return jsonify(new_kunde), 201
    return jsonify(kunden)

@app.route('/kunden/<int:kunden_id>', methods=['GET', 'PUT', 'DELETE'])
def kunden_details(kunden_id):
    k = next((k for k in kunden if k['id'] == kunden_id), None)
    if request.method == 'GET':
        return jsonify(k)
    elif request.method == 'PUT':
        data = request.json
        k.update(data)
        return jsonify(k)
    elif request.method == 'DELETE':
        kunden.remove(k)
        return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
