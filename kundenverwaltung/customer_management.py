from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'mysql-customer'),
        user=os.environ.get('MYSQL_USER', 'customer_user'),
        password=os.environ.get('MYSQL_PASSWORD', 'Customer1'),
        database=os.environ.get('MYSQL_DATABASE', 'customer_db')
    )

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO customers (name, email, password) VALUES (%s, %s, %s)",
        (data['name'], data['email'], data['password'])
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "Customer registered successfully"}), 201

@app.route('/customers', methods=['GET'])
def get_customers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(customers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
