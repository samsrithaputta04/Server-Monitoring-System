from flask import Flask, render_template_string
import psutil
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
app = Flask(__name__)
CPU_THRESHOLD = 80       # %
MEM_THRESHOLD = 80       # %
DISK_THRESHOLD = 80      # %
LOG_FILE = "/var/log/server_monitor.log"
load_dotenv() 
EMAIL_FROM = "Server Monitoring"
EMAIL_TO = "217r1a05h5@cmrtc.ac.in"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "surnasrikanth123@gmail.com"
EMAIL_PASS = os.environ.get('emailpass')
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Server Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1e1e1e; color: #eee; text-align: center; }
        h1 { color: #00d1b2; }
        .card { background: #2a2a2a; border-radius: 10px; padding: 20px; margin: 20px auto; width: 300px; }
        .metric { font-size: 1.5em; margin: 10px 0; }
        .ok { color: lightgreen; }
        .warn { color: orange; }
        .alert { color: red; }
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>📊 Server Monitoring Dashboard</h1>
    <div class="card">
        <div class="metric">CPU Usage: <span class="{{ cpu_class }}">{{ cpu }}%</span></div>
        <div class="metric">Memory Usage: <span class="{{ mem_class }}">{{ mem }}%</span></div>
        <div class="metric">Disk Usage: <span class="{{ disk_class }}">{{ disk }}%</span></div>
        <div class="metric">Last Update: {{ time }}</div>
    </div>
</body>
</html>
"""

def get_status_class(value):
    if value < 50:
        return "ok"
    elif value < 80:
        return "warn"
    else:
        return "alert"



def send_email_alert(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Email sending failed: {e}")
def check_metrics(cpu_usage,mem_usage,disk_usage):
    # cpu_usage = psutil.cpu_percent(interval=1)
    # mem_usage = psutil.virtual_memory().percent
    # disk_usage = psutil.disk_usage("/").percent


    if cpu_usage > CPU_THRESHOLD:
        send_email_alert("CPU Alert", f"CPU usage is at {cpu_usage}%")

    if mem_usage > MEM_THRESHOLD:
        send_email_alert("Memory Alert", f"Memory usage is at {mem_usage}%")

    if disk_usage > DISK_THRESHOLD:
        send_email_alert("Disk Alert", f"Disk usage is at {disk_usage}%")


@app.route("/")
def index():
    cpu_usage = psutil.cpu_percent(interval=0.1)
    mem_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    check_metrics(cpu_usage,mem_usage,disk_usage)
    return render_template_string(
        TEMPLATE,
        cpu=cpu_usage,
        mem=mem_usage,
        disk=disk_usage,
        cpu_class=get_status_class(cpu_usage),
        mem_class=get_status_class(mem_usage),
        disk_class=get_status_class(disk_usage),
        time=now
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
