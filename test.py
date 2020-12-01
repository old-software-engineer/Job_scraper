import psycopg2, os

pg_user = os.getenv('POSTGRES_USER')
pg_pass = os.getenv('POSTGRES_PASSWORD')
pg_db = 'job_portal_production'

conn = psycopg2.connect( host = "127.0.0.1",
                         port = "5432",
                         user=pg_user,
                         password=pg_pass,
                         dbname=pg_db )
cursor = conn.cursor()
# Print PostgreSQL Connection properties
print ( conn.get_dsn_parameters(),"\n")


def get_jobs():
    query = f"select id, uid, title, publish_date from jobs where publish_date='2020-09-23'"
    cursor.execute(query)
    jobs = cursor.fetchall()
    print(len(jobs), 'No of jobs present in database.')
    return jobs




jobs = get_jobs()
print(jobs[0])
#f = open('duplicates.txt', 'a', encoding="utf-8")
#duplicates = 0
#original  = []
#for job in jobs:
 #   if job[1] in original:
 #       duplicates += 1
  #      f.write(str(job) + '\n')
        # cursor.execute("DELETE FROM jobs WHERE id= " + str(job[0]))
        # conn.commit()
   # else:
   #     original.append(job[1])
#f.close()
#print(duplicates, 'Duplicate records')
#print(len(original), 'No of original records.')
