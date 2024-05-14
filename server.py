from flask import Flask, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

def needs_pill_today():
	today = datetime.now().date()
	start_date = datetime(2024, 5, 12)
	days_since_start = (today - start_date).days
	return days_since_start % 2 == 0

@app.route('/')
def index():
	needs_pill = needs_pill_today()
	return render_template('index.html', needs_pill=needs_pill)

if __name__ == '__main__':
	app.run(debug=True)
