from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import os
import subprocess
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'scripts'
app.config['ALLOWED_EXTENSIONS'] = {'py'}

# Create a scheduler instance
scheduler = BackgroundScheduler()
scheduler.start()  # Start scheduler here

script_status = {}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def run_script(script_path):
    script_name = os.path.basename(script_path)
    script_status[script_name] = {'status': 'Running', 'last_run': None}
    subprocess.run(['python', script_path])
    script_status[script_name] = {'status': 'Completed', 'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

@app.route('/')
def index():
    scripts = os.listdir(app.config['UPLOAD_FOLDER'])
    jobs = scheduler.get_jobs()
    # Format the next_run_time for better readability
    formatted_jobs = []
    for job in jobs:
        next_run_time = job.next_run_time
        if next_run_time:
            # Convert to local time and format
            local_time = next_run_time.astimezone(pytz.timezone('Europe/London'))
            formatted_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
            formatted_jobs.append({
                'id': job.id,
                'next_run_time': formatted_time
            })
    return render_template('index.html', scripts=scripts, jobs=formatted_jobs, script_status=script_status)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'status': 'success', 'message': 'File uploaded successfully!'}), 200
    return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

@app.route('/run-script', methods=['POST'])
def run_script_route():
    script_name = request.form['script_name']
    script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_name)
    run_script(script_path)
    return jsonify({'status': 'success', 'message': f'Script {script_name} started!'}), 200

@app.route('/schedule-script', methods=['POST'])
def schedule_script():
    script_name = request.form['script_name']
    interval = request.form.get('interval')
    day = request.form.get('day')
    time_str = request.form.get('time')
    script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_name)

    # Remove existing job if it exists
    existing_jobs = scheduler.get_jobs()
    for job in existing_jobs:
        if job.name == script_name:
            scheduler.remove_job(job.id)

    if interval:
        scheduler.add_job(run_script, IntervalTrigger(minutes=int(interval)), args=[script_path], id=script_name, name=script_name)
    elif day and time_str:
        day_of_week = day.lower()
        time = datetime.strptime(time_str, '%H:%M').time()
        scheduler.add_job(run_script, CronTrigger(day_of_week=day_of_week, hour=time.hour, minute=time.minute), args=[script_path], id=script_name, name=script_name)
    
    return jsonify({'status': 'success', 'message': f'Script {script_name} scheduled!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
