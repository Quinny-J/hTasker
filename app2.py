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
script_versions = {}
logs = []
performance_data = {}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def run_script(script_path, *args):
    script_name = os.path.basename(script_path)
    script_status[script_name] = {'status': 'Running', 'last_run': None}
    start_time = datetime.now()
    command = ['python', script_path] + list(args)
    result = subprocess.run(command, capture_output=True, text=True)
    end_time = datetime.now()
    script_status[script_name] = {'status': 'Completed', 'last_run': end_time.strftime('%Y-%m-%d %H:%M:%S')}
    logs.append({'script': script_name, 'output': result.stdout, 'timestamp': end_time.strftime('%Y-%m-%d %H:%M:%S')})
    performance_data[script_name] = {'start_time': start_time, 'end_time': end_time, 'duration': (end_time - start_time).total_seconds()}

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
    return render_template('dashboard.html', scripts=scripts, jobs=formatted_jobs, script_status=script_status, logs=logs, performance_data=performance_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        version = script_versions.get(filename, 0) + 1
        script_versions[filename] = version
        versioned_filename = f"{filename.rsplit('.', 1)[0]}_v{version}.py"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], versioned_filename))
        return jsonify({'status': 'success', 'message': 'File uploaded successfully!'}), 200
    return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

@app.route('/run-script', methods=['POST'])
def run_script_route():
    script_name = request.form['script_name']
    arguments = request.form.get('arguments', '').split()  # Split by spaces for multiple arguments
    script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_name)
    run_script(script_path, *arguments)
    return f"Script {script_name} started with arguments: {', '.join(arguments)}!"

@app.route('/schedule-script', methods=['POST'])
def schedule_script():
    script_name = request.form['script_name']
    interval = request.form.get('interval')
    day = request.form.get('day')
    time_str = request.form.get('time')
    arguments = request.form.get('arguments', '').split()  # Split by spaces for multiple arguments
    script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_name)
    
    def scheduled_run_script():
        run_script(script_path, *arguments)
    
    if interval:
        scheduler.add_job(scheduled_run_script, 'interval', minutes=int(interval), id=f'interval_{script_name}')
    elif day and time_str:
        day_of_week = day.lower()
        time = datetime.strptime(time_str, '%H:%M').time()
        scheduler.add_job(scheduled_run_script, 'cron', day_of_week=day_of_week, hour=time.hour, minute=time.minute, id=f'cron_{script_name}')
    
    scheduler.start()
    return redirect(url_for('index'))

@app.route('/cancel-job/<job_id>', methods=['POST'])
def cancel_job(job_id):
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)
        return redirect(url_for('index', message=f"Job {job_id} canceled!"))
    return redirect(url_for('index', message=f"Job {job_id} not found!"))

@app.route('/logs')
def get_logs():
    return render_template('logs.html', logs=logs)

@app.route('/api/docs')
def api_docs():
    return render_template('api_docs.html')

if __name__ == '__main__':
    app.run(debug=True)
