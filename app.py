from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from urllib.parse import urlparse

# Initialize Flask app and SQLAlchemy
app = Flask(__name__)

# Configure database URI for Heroku ClearDB or local database
db_url = urlparse(os.getenv('CLEARDB_DATABASE_URL', 'mysql://flaskuser:password@localhost/todo_db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_url.username}:{db_url.password}@{db_url.hostname}/{db_url.path[1:]}"
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

    return render_template('calendar.html', month_name=today.strftime('%B'), year=year, month=month, month_days=month_days)

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

    # Handle AJAX requests for dynamic content loading
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('todo.html', todos=tasks)

    # Render the full page otherwise
    return render_template('todo.html', month_name=str(month), year=year, day=day, todos=tasks)

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
    app.run(debug=True)
