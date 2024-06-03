from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="mysql-room",
        user="room_user",
        password="room_password",
        database="room_db"
    )

@app.route('/rooms', methods=['POST'])
def add_room():
    data = request.get_json()
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO rooms (number, type, price, available) VALUES (%s, %s, %s, %s)",
        (data['number'], data['type'], data['price'], data['available'])
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Room added successfully"}), 201

@app.route('/rooms', methods=['GET'])
def get_rooms():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(rooms)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
