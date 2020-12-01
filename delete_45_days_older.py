import datetime
from dateutil.relativedelta import relativedelta
import psycopg2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


# ***************  For developer use only  **************

# pg_user = 'postgres'
# pg_pass = '1234'
# pg_db = 'postgres'

# ***************  For server use only  **************

pg_user = os.getenv('POSTGRES_USER')
pg_pass = os.getenv('POSTGRES_PASSWORD')
pg_db = 'job_portal_production'

# ***************   for server use ends   ***************

def get_total_jobs():
    query = f"select id from jobs"
    cursor.execute(query)
    jobs = cursor.fetchall()
    print(len(jobs), 'No of jobs present in database.')
    return len(jobs)

def get_older_jobs(QUERY_DATE):
    query = f"select id, publish_date from jobs where publish_date < '{QUERY_DATE}'"
    cursor.execute(query)
    jobs = cursor.fetchall()
    return len(jobs)

def send_mail(_mail, currentSubject,currentMsg):
    try:
        msg = MIMEMultipart()
        message = currentMsg
        username = "ankit@codegaragetech.com"
        password = "ankit@codegaragetech.com"
        smtphost = "smtp.gmail.com:587"
        msg["From"] = "ankit@codegaragetech.com"
        msg["To"] = _mail
        msg["Subject"] = currentSubject
        msg.attach(MIMEText(message, 'html'))
        server = smtplib.SMTP(smtphost)
        server.starttls()
        server.login(username, password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print('Sent mail successfully')
    except:
        print('Unable to send mail')
    finally:
        server.quit()

conn = psycopg2.connect(host="127.0.0.1",
                            port="5432",
                            user=pg_user,
                            password=pg_pass,
                            dbname=pg_db)
cursor = conn.cursor()
# Print PostgreSQL Connection properties
print(conn.get_dsn_parameters(), "\n")

total_jobs = get_total_jobs()

today = datetime.date.today()
QUERY_DATE = str(today - relativedelta(days=45))
print('Query Date : ', QUERY_DATE)

older_jobs = get_older_jobs(QUERY_DATE)
print('Older Jobs : ', older_jobs)

try:
    cursor.execute(f"DELETE FROM jobs WHERE publish_date < '{QUERY_DATE}'")
    conn.commit()
    print('Deleted successfully.')
    print('Jobs left after deletion : ', total_jobs - older_jobs)
    msg = f"""Older jobs deletion update =>
              <br/> Total Jobs before deletion : {total_jobs}
              <br/> Jobs older than 45 days : {older_jobs}
              <br/> Total jobs after deletion : {total_jobs-older_jobs}"""
    send_mail('ankitmahajan478@gmail.com', 'Indeed jobs Deletion update : ', msg)
except:
    print('Failed to delete')
    msg = f""" Script has failed to delete older records."""
    send_mail('ankitmahajan478@gmail.com', 'Indeed jobs Deletion update : ', msg)


