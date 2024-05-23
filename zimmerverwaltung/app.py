from flask import Flask, request, jsonify

app = Flask(__name__)

zimmer = []

@app.route('/zimmer', methods=['GET', 'POST'])
def manage_zimmer():
    if request.method == 'POST':
        new_zimmer = request.json
        zimmer.append(new_zimmer)
        return jsonify(new_zimmer), 201
    return jsonify(zimmer)

@app.route('/zimmer/<int:zimmer_id>', methods=['GET', 'PUT', 'DELETE'])
def zimmer_details(zimmer_id):
    z = next((z for z in zimmer if z['id'] == zimmer_id), None)
    if request.method == 'GET':
        return jsonify(z)
    elif request.method == 'PUT':
        data = request.json
        z.update(data)
        return jsonify(z)
    elif request.method == 'DELETE':
        zimmer.remove(z)
        return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
