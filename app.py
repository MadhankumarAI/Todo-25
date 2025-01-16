from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from urllib.parse import urlparse

# Initialize Flask app and SQLAlchemy
app = Flask(__name__)

# Configure database URI for PostgreSQL (Render)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://todo_cjrn_user:WYIB18RMzFaqZNABkS1huUHfjnSlE4bp@dpg-cu4e2ql6l47c73b22h00-a/todo_cjrn')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://todo_cjrn_user:WYIB18RMzFaqZNABkS1huUHfjnSlE4bp@dpg-cu4e2ql6l47c73b22h00-a/todo_cjrn'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the ToDo model
class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(50), nullable=False)  # Date formatted as 'YYYY-MM-DD'

    def __repr__(self):
        return f'<ToDo {self.id} - {self.task}>'

# Create tables if they don't exist
def create_table():
    with app.app_context():
        db.create_all()

# Route for the calendar page
@app.route('/')
def index():
    today = datetime.today()
    month = today.month
    year = today.year
    month_days = generate_month_days(month, year)

    return render_template('index.html', month_name=today.strftime('%B'), year=year, month=month, month_days=month_days)

# Route for a specific day's to-do list
@app.route('/todo/<int:month>/<int:year>/<int:day>', methods=['GET', 'POST'])
def todo_list(month, year, day):
    date_key = f"{year}-{month:02d}-{day:02d}"

    # If POST request, add new to-do item
    if request.method == 'POST':
        task = request.form.get('task')
        if task:
            new_task = ToDo(task=task, date=date_key)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for('todo_list', month=month, year=year, day=day))

    # Fetch all tasks for the selected date
    tasks = ToDo.query.filter_by(date=date_key).all()

    # Handle AJAX requests for task list
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('task_list.html', todos=tasks)

    return render_template('todo.html', month_name=str(month), year=year, day=day, todos=tasks)

# Route to delete a specific task
@app.route('/delete-task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = ToDo.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    else:
        return jsonify({'message': 'Task not found'}), 404


# Helper function to generate days for the current month
def generate_month_days(month, year):
    from calendar import monthrange
    first_day, num_days = monthrange(year, month)
    
    month_days = []
    week = [''] * first_day
    for day in range(1, num_days + 1):
        week.append(day)
        if len(week) == 7:
            month_days.append(week)
            week = []
    if week:
        month_days.append(week)
    
    return month_days

if __name__ == '__main__':
    create_table()
    app.run(debug=False)
