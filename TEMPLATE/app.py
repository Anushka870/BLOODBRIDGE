import mysql.connector
from flask import Flask, request, jsonify, render_template
import time

app = Flask(__name__)

# --- MySQL Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234'  # <-- Change this to your MySQL password
}
DB_NAME = 'bloodbridge'

def get_db_connection():
    config_with_db = DB_CONFIG.copy()
    config_with_db['database'] = DB_NAME
    try:
        return mysql.connector.connect(**config_with_db)
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    try:
        # Create database if it doesn't exist
        temp_conn = mysql.connector.connect(**DB_CONFIG)
        cursor = temp_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.close()
        temp_conn.close()

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. DROP OLD TABLES (Forces schema to update with new columns)
        cursor.execute("DROP TABLE IF EXISTS requests")
        cursor.execute("DROP TABLE IF EXISTS donors")
        cursor.execute("DROP TABLE IF EXISTS blood_banks")

        # 2. CREATE FRESH TABLES
        cursor.execute('''
            CREATE TABLE donors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(20) UNIQUE NOT NULL,
                bg VARCHAR(10) NOT NULL,
                city VARCHAR(100) NOT NULL,
                pin VARCHAR(20) NOT NULL,
                times INT DEFAULT 0,
                distance FLOAT DEFAULT 3.0,
                available BOOLEAN DEFAULT TRUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE blood_banks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(20) UNIQUE NOT NULL,
                city VARCHAR(100) NOT NULL,
                pin VARCHAR(20) NOT NULL,
                distance FLOAT DEFAULT 3.5,
                a_pos FLOAT DEFAULT 0.0, a_neg FLOAT DEFAULT 0.0,
                b_pos FLOAT DEFAULT 0.0, b_neg FLOAT DEFAULT 0.0,
                ab_pos FLOAT DEFAULT 0.0, ab_neg FLOAT DEFAULT 0.0,
                o_pos FLOAT DEFAULT 0.0, o_neg FLOAT DEFAULT 0.0
            )
        ''')

        cursor.execute('''
            CREATE TABLE requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient VARCHAR(255) NOT NULL,
                hospital VARCHAR(255) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                bg VARCHAR(10) NOT NULL,
                city VARCHAR(100) NOT NULL,
                pin VARCHAR(20) NOT NULL,
                liters FLOAT NOT NULL,
                urgency VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'open',
                created_at BIGINT,
                expires_at BIGINT
            )
        ''')
        
        # 3. POPULATE DUMMY DATA
        donors_data = [
            ('Aarav Sharma', '9876543210', 'O+', 'Delhi', '110001', 7, 1.8, 1),
            ('Priya Patel', '9988776655', 'A-', 'Delhi', '110017', 2, 7.5, 0),
            ('Rohan Verma', '8877665544', 'B+', 'Delhi', '110005', 5, 4.8, 1),
            ('Sneha Iyer', '7766554433', 'AB+', 'Delhi', '110016', 1, 3.2, 1),
            ('Vikramjit Singh', '9123456789', 'O-', 'Delhi', '110024', 8, 5.9, 1),
            ('Ananya Deshmukh', '9811223344', 'B-', 'Delhi', '110070', 3, 9.2, 1),
            ('Devendra Mehra', '9899001122', 'A+', 'Delhi', '110085', 4, 13.4, 1),
            ('Simran Kaur', '9711556677', 'AB-', 'Delhi', '110027', 1, 8.1, 1),
            ('Harshit Saxena', '9654112233', 'O+', 'Delhi', '110091', 6, 6.7, 1),
            ('Tanvi Agarwal', '9540889900', 'B+', 'Delhi', '110052', 2, 7.1, 1),
            ('Naveen Jindal', '9910224466', 'A+', 'Delhi', '110003', 9, 3.5, 0)
        ]
        cursor.executemany("INSERT INTO donors (name, phone, bg, city, pin, times, distance, available) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", donors_data)

        banks_data = [
            ('Central Red Cross Blood Center', '1122334455', 'Delhi', '110001', 2.2, 6.0, 2.5, 4.5, 1.5, 2.0, 0.5, 14.0, 4.0),
            ('Apex Hospital Blood Bank', '1133557799', 'Delhi', '110017', 8.0, 3.5, 1.0, 5.0, 0.5, 2.0, 0.0, 9.0, 2.0),
            ('Rotary Blood Bank', '1144668800', 'Delhi', '110049', 5.1, 4.0, 0.5, 6.0, 2.0, 1.5, 1.0, 11.0, 3.5),
            ('Northern Railway Central Hospital Bank', '1155779911', 'Delhi', '110055', 3.4, 2.0, 0.0, 3.5, 0.5, 0.5, 0.0, 5.0, 1.0)
        ]
        cursor.executemany("INSERT INTO blood_banks (name, phone, city, pin, distance, a_pos, a_neg, b_pos, b_neg, ab_pos, ab_neg, o_pos, o_neg) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", banks_data)

        now = int(time.time() * 1000)
        reqs_data = [
            ('Rahul Verma', 'AIIMS Delhi', '9998887776', 'O+', 'Delhi', '110029', 2.0, 'Critical (Within 2 Hours)', 'open', now - 3000000, now + 4200000),
            ('Deepak Chopra', 'Safdarjung Hospital', '8887776665', 'O+', 'Delhi', '110016', 0.7, 'Urgent (Within 6 Hours)', 'open', now - 18000000, now + 2100000)
        ]
        cursor.executemany("INSERT INTO requests (patient, hospital, phone, bg, city, pin, liters, urgency, status, created_at, expires_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", reqs_data)

        conn.commit()
        cursor.close()
        conn.close()
        print("Database schema successfully recreated and populated!")
    except Exception as e:
        print(f"Database Initialization Error: {e}")

# --- API Routes ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/directory", methods=["GET"])
def get_directory():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM donors")
        donors = cursor.fetchall()
        
        cursor.execute("SELECT * FROM blood_banks")
        banks_raw = cursor.fetchall()
        
        cursor.close()
        conn.close()

        banks = []
        for b in banks_raw:
            banks.append({
                "id": b["id"], "name": b["name"], "phone": b["phone"], "city": b["city"], "pin": b["pin"], "distance": b["distance"],
                "stock": {
                    "A+": b["a_pos"], "A-": b["a_neg"], "B+": b["b_pos"], "B-": b["b_neg"],
                    "AB+": b["ab_pos"], "AB-": b["ab_neg"], "O+": b["o_pos"], "O-": b["o_neg"]
                }
            })

        return jsonify({"donors": donors, "banks": banks})
    except Exception as e:
        return jsonify({"donors": [], "banks": [], "error": str(e)})

@app.route("/api/donors", methods=["POST"])
def add_donor():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO donors (name, phone, bg, city, pin, times, distance, available)
            VALUES (%s, %s, %s, %s, %s, %s, 3.0, 1)
        ''', (data['name'], data['phone'], data['bg'], data['city'], data['pin'], data.get('times', 0)))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/blood-banks", methods=["POST"])
def add_bank():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO blood_banks (name, phone, city, pin, distance)
            VALUES (%s, %s, %s, %s, 3.5)
        ''', (data['name'], data['phone'], data['city'], data['pin']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/requests", methods=["POST"])
def add_request():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (patient, hospital, phone, bg, city, pin, liters, urgency, status, created_at, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'open', %s, %s)
        ''', (data['patient'], data['hospital'], data['phone'], data['bg'], data['city'], data['pin'], data['liters'], data['urgency'], data['createdAt'], data['expiresAt']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/profile/<phone>", methods=["GET"])
def get_profile(phone):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM donors WHERE phone = %s", (phone,))
        donor = cursor.fetchone()
        if donor:
            cursor.close()
            conn.close()
            return jsonify({"role": "donor", "user": donor})

        cursor.execute("SELECT * FROM blood_banks WHERE phone = %s", (phone,))
        bank = cursor.fetchone()
        if bank:
            stock = {
                "A+": bank["a_pos"], "A-": bank["a_neg"], "B+": bank["b_pos"], "B-": bank["b_neg"],
                "AB+": bank["ab_pos"], "AB-": bank["ab_neg"], "O+": bank["o_pos"], "O-": bank["o_neg"]
            }
            bank["stock"] = stock
            cursor.close()
            conn.close()
            return jsonify({"role": "bank", "user": bank})

        cursor.execute("SELECT * FROM requests WHERE phone = %s", (phone,))
        requests_data = cursor.fetchall()
        if requests_data:
            cursor.close()
            conn.close()
            return jsonify({"role": "receiver", "requests": requests_data})

        cursor.close()
        conn.close()
        return jsonify({"role": None, "message": "Phone number not found."}), 404
    except Exception as e:
        return jsonify({"role": None, "message": str(e)}), 400

@app.route("/api/donors/<int:id>", methods=["PUT"])
def update_donor(id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE donors SET name = %s, city = %s, pin = %s, times = %s, available = %s
            WHERE id = %s
        ''', (data['name'], data['city'], data['pin'], data['times'], 1 if data['available'] else 0, id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/blood-banks/<int:id>", methods=["PUT"])
def update_bank(id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE blood_banks 
            SET a_pos = %s, a_neg = %s, b_pos = %s, b_neg = %s, ab_pos = %s, ab_neg = %s, o_pos = %s, o_neg = %s
            WHERE id = %s
        ''', (data['A+'], data['A-'], data['B+'], data['B-'], data['AB+'], data['AB-'], data['O+'], data['O-'], id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM requests WHERE status = 'open'")
        reqs = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(reqs)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/requests/<int:id>/resolve", methods=["POST"])
def resolve_request(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE requests SET status = 'resolved' WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)