import mysql.connector
from mysql.connector import Error
import time

def setup_mysql_database():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1234' # <-- CHANGE TO YOUR MYSQL PASSWORD
    }

    try:
        # 1. Connect and create database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS bloodbridge")
        cursor.close()
        conn.close()

        # 2. Connect to the new database
        db_config['database'] = 'bloodbridge'
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 3. Create Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS donors (
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
            CREATE TABLE IF NOT EXISTS blood_banks (
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
            CREATE TABLE IF NOT EXISTS requests (
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

        # 4. Clear existing data to prevent duplicates on rerun
        cursor.execute("DELETE FROM donors")
        cursor.execute("DELETE FROM blood_banks")
        cursor.execute("DELETE FROM requests")
        
        # Reset Auto-Increments
        cursor.execute("ALTER TABLE donors AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE blood_banks AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE requests AUTO_INCREMENT = 1")

        # 5. Insert Donors
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
        cursor.executemany('''
            INSERT INTO donors (name, phone, bg, city, pin, times, distance, available)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', donors_data)

        # 6. Insert Blood Banks
        banks_data = [
            ('Central Red Cross Blood Center', '1122334455', 'Delhi', '110001', 2.2, 6.0, 2.5, 4.5, 1.5, 2.0, 0.5, 14.0, 4.0),
            ('Apex Hospital Blood Bank', '1133557799', 'Delhi', '110017', 8.0, 3.5, 1.0, 5.0, 0.5, 2.0, 0.0, 9.0, 2.0),
            ('Rotary Blood Bank', '1144668800', 'Delhi', '110049', 5.1, 4.0, 0.5, 6.0, 2.0, 1.5, 1.0, 11.0, 3.5),
            ('Northern Railway Central Hospital Bank', '1155779911', 'Delhi', '110055', 3.4, 2.0, 0.0, 3.5, 0.5, 0.5, 0.0, 5.0, 1.0)
        ]
        cursor.executemany('''
            INSERT INTO blood_banks (name, phone, city, pin, distance, a_pos, a_neg, b_pos, b_neg, ab_pos, ab_neg, o_pos, o_neg)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', banks_data)

        # 7. Insert Active Requests
        now = int(time.time() * 1000)
        reqs_data = [
            ('Rahul Verma', 'AIIMS Delhi', '9998887776', 'O+', 'Delhi', '110029', 2.0, 'Critical (Within 2 Hours)', 'open', now - (50 * 60 * 1000), now + (70 * 60 * 1000)),
            ('Deepak Chopra', 'Safdarjung Hospital', '8887776665', 'O+', 'Delhi', '110016', 0.7, 'Urgent (Within 6 Hours)', 'open', now - (5 * 3600 * 1000), now + (35 * 60 * 1000))
        ]
        cursor.executemany('''
            INSERT INTO requests (patient, hospital, phone, bg, city, pin, liters, urgency, status, created_at, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', reqs_data)

        conn.commit()
        print("MySQL Database 'bloodbridge' populated successfully!")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_mysql_database()