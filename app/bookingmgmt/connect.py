import psycopg2

def connect_to_db(dbname):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user="ubuntu",
            password="ubuntu",  # Anpassen
            host="localhost",
            port=5432
        )
        return conn
    except psycopg2.Error as e:
        print(f"Fehler bei der Verbindung zur bpf_bookings-Datenbank: {e}")
        return None
