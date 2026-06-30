import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create primary unified users table structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('donor', 'admin')),
            blood_group TEXT,
            phone TEXT,
            latitude REAL,
            longitude REAL,
            is_available INTEGER DEFAULT 1,
            donation_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inject Mock Data Profiles for testing features instantly
    try:
        mock_users = [
            # Default Administrator Account (Password: admin123)
            ('System Admin', 'admin@bloodlink.com', 'admin123', 'admin', None, None, None, None, 0, 0),
            
            # Sample Donors with distinct locations around Visakhapatnam and donation counts
            ('Ravi Kumar', 'ravi@gmail.com', 'pass123', 'donor', 'O+', '9876543210', 17.6896, 83.2185, 1, 12),  # Gold Badge
            ('Kavya Reddi', 'kavya@gmail.com', 'pass123', 'donor', 'A+', '8765432109', 17.7120, 83.3240, 1, 6),   # Silver Badge
            ('Deelip Naidu', 'deelip@gmail.com', 'pass123', 'donor', 'B+', '7654321098', 17.7250, 83.2950, 1, 2),  # Bronze Badge
            ('Mounika P.', 'mounika@gmail.com', 'pass123', 'donor', 'O+', '6543210987', 17.6750, 83.1900, 1, 0)   # New Donor
        ]
        
        cursor.executemany('''
            INSERT INTO users (name, email, password, role, blood_group, phone, latitude, longitude, is_available, donation_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', mock_users)
        
        conn.commit()
        print("🎉 Database initialized successfully with admin and mock donor profiles!")
    except sqlite3.IntegrityError:
        print("⚠️ Database tables already exist and contain data record baselines.")
        
    conn.close()

if __name__ == '__main__':
    init_db()