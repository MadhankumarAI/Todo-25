from flask import Flask, request, render_template, redirect, url_for
import os
import mysql.connector
from urllib.parse import urlparse

app = Flask(__name__)

# Parse ClearDB URL from environment variable (for Heroku)
db_url = urlparse(os.getenv('CLEARDB_DATABASE_URL', 'mysql://root:password@localhost/todo'))

# Database configuration
db_config = {
    'host': db_url.hostname,
    'user': db_url.username,
    'password': db_url.password,
    'database': db_url.path[1:],  # Remove leading '/'
}

# Initialize database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Create tables if they don't exist
def create_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS todos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        task VARCHAR(255) NOT NULL,
        date DATE NOT NULL
    )''')
    connection.commit()
    connection.close()

# Routes
@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM todos ORDER BY date ASC')
    todos = cursor.fetchall()
    connection.close()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    task = request.form['task']
    date = request.form['date']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO todos (task, date) VALUES (%s, %s)', (task, date))
    connection.commit()
    connection.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
