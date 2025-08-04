
def save_medical_history(history_entry):
    """Save medical history to database"""
    # Connect to your database (this is a placeholder)
    # You might use SQLite, PostgreSQL, MongoDB, etc.
    
    # Example using SQLite
    import sqlite3
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medical_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        timestamp TEXT,
        symptoms TEXT,
        possible_diseases TEXT
    )
    ''')
    
    # Insert history entry
    cursor.execute('''
    INSERT INTO medical_history (user_id, timestamp, symptoms, possible_diseases)
    VALUES (?, ?, ?, ?)
    ''', (
        history_entry["user_id"],
        history_entry["timestamp"],
        json.dumps(history_entry["symptoms"]),
        json.dumps(history_entry["possible_diseases"])
    ))
    
    conn.commit()
    conn.close()