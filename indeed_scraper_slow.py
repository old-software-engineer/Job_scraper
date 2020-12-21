# -*- coding: utf-8 -*-

from selenium import webdriver
import os,time,datetime
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException,ElementNotInteractableException,ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import psycopg2
import urllib.request as urllib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ***************  For developer use only  **************

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximised")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--window-size=1920,1080")

pg_user = 'av'
pg_pass = 'azad'
pg_db = 'test_nelmon'
# ***************  For server use only  **************
#
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("--start-maximised")
#
# pg_user = os.getenv('POSTGRES_USER')
# pg_pass = os.getenv('POSTGRES_PASSWORD')
# pg_db = 'job_portal_production'
#
# ***************   for server use ends   ***************

print(datetime.datetime.now(), 'Starting script time')

keywords = ['Accounting', 'Finance', 'Banking', 'construction', 'Real+estate', 'Building', 'Engineering', 'Supply+chain',
            'Logistics', 'Inventory', 'Manufacturing', 'Operation', 'Administration', 'Office', 'Assistant',
            'Information+technology', 'hi-tech', 'Software', 'development', 'Hardware', 'Machinery', 'Health+care',
            'Medicine', 'Pharmaceutical', 'Cannabis', 'Production', 'Transportation', 'work', 'job', 'law', 'legal',
            'service', 'restaurant', 'accommodation', 'hotel', 'human+resources', 'culture', 'recruitment', 'hiring',
            'position']

# keywords = ['Accounting']

state_short = {'NL':'Newfoundland and Labrador', 'PE':'Prince Edward Island' ,'NS':'Nova Scotia',
                'NB' : 'New Brunswick', 'QC':'Quebec', 'ON' : 'Ontario', 'MB' : 'Manitoba', 'SK':'Saskatchewan',
               'AB':'Alberta', 'BC':'British Columbia', 'YT':'Yukon', 'NT':'Northwest Territories', 'NU':'Nunavut'}

conn = psycopg2.connect( host = "127.0.0.1",
                         port = "5432",
                         user=pg_user,
                         password=pg_pass,
                         dbname=pg_db )
cursor = conn.cursor()
# Print PostgreSQL Connection properties
print ( conn.get_dsn_parameters(),"\n")

def send_mail(_mail, currentSubject,currentMsg):
    try:
        msg = MIMEMultipart()
        message = currentMsg
        username = "azadveer@codegaragetech.com"
        password = "azadveer@123"
        smtphost = "smtp.gmail.com:587"
        msg["From"] = "azadveer@codegaragetech.com"
        msg["To"] = _mail
        msg["Subject"] = currentSubject
        msg.attach(MIMEText(message, 'html'))


        # -------------INCLUDE THIS FOR ATTACHMENT------------------
        # open the file to be sent
        filename = "summary.log"
        attachment = open("summary.log", "rb")

        # instance of MIMEBase and named as p
        p = MIMEBase('application', 'octet-stream')

        # To change the payload into encoded form
        p.set_payload((attachment).read())

        # encode into base64
        encoders.encode_base64(p)

        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # attach the instance 'p' to instance 'msg'
        msg.attach(p)

        # -------------INCLUDE THIS FOR ATTACHMENT ENDS------------------

        server = smtplib.SMTP(smtphost)
        server.ehlo()
        server.starttls()
        server.login(user=username,password=password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print('Sent mail successfully')
    except:
        print('Unable to send mail')
    finally:
        server.quit()

def getJobsDiv(driver, num):
    try:
        if num == 10:
            num = 1
            driver.refresh()
            time.sleep(3)
        job_divs = driver.find_elements_by_class_name('jobsearch-SerpJobCard')
        time.sleep(3)
        print(len(job_divs), 'Number of jobs in a page.')
        if (len(job_divs) == 0):
            results = no_results_check(driver)
            time.sleep(3)
            summary.write('Checking if there are any jobs for this keyword : ' + results)
            if results == 'no_results':
                return 'no_jobs'
            return getJobsDiv(driver, num+1)
        else:
            return job_divs
    except:
        checkWindowHandles(driver)
        time.sleep(2)
        return getJobsDiv(driver, num+1)

def checkWindowHandles(driver):
    if len(driver.window_handles) > 1:
        time.sleep(3)
        tabs = len(driver.window_handles)
        for h in range(1, tabs-1):
            print('closing a tab : ', h)
            driver.switch_to.window(driver.window_handles[h])
            driver.close()
            time.sleep(3)
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[0])

def checkPopOver(driver):
    try:
        div = driver.find_element_by_id('popover-foreground')
        time.sleep(3)
        div.find_element_by_class_name('popover-x-button-close').click()
        time.sleep(3)
    except:
        pass

def no_results_check(driver):
    try:
        driver.find_element_by_class_name('no_results')
        time.sleep(3)
        return 'no_results'
    except:
        return('none')

def checkCookieBox(driver):
    try:
        div = driver.find_element_by_class_name('icl-LegalConsentBanner-action')
        div.find_element_by_class_name('tos-Button').click()
        time.sleep(3)
    except:
        pass

def checkCompanyLink(driver, job, i):
    try:
        apply_div = driver.find_element_by_id('apply-button-container')
        try:
            apply_text = apply_div.find_element_by_class_name('view-apply-button').text.strip()
            if apply_text != 'Apply On Company Site':
                print('Company website link is not available')
                return 'continue'
            else:
                company_url = driver.find_element_by_class_name('view-apply-button').get_attribute('href')
                print(company_url, 'company url')
                return company_url
        except:
            return 'continue'

    except:
        if i > 10:
            i=1
            return 'continue'
        checkPopOver(driver)
        checkCookieBox(driver)
        time.sleep(3)
        print('Retrying company link button')
        return checkCompanyLink(driver, job, i+1)

def getJobIdsfromDB():
    query = f"select uid from jobs"
    cursor.execute(query)
    origin_IDs = cursor.fetchall()
    print(len(origin_IDs), 'No of jobs present in database.')
    return origin_IDs

def checkJobIdsfromDB(uid):
    query = f"""select id from jobs where uid='{uid}'"""
    cursor.execute(query)
    origin_IDs = cursor.fetchall()
    print(len(origin_IDs), 'No jobs with this uid ', uid)
    return origin_IDs

def get_company_details():
    query = f"select name from companies"
    cursor.execute(query)
    companies = cursor.fetchall()
    print(len(companies), 'No of jobs present in database.')
    return companies

def getCompanyId(company):
    print('Company in get company function : ',company)
    query = '''select id from companies where name= %s '''
    cursor.execute(query,(company,))
    company_id = cursor.fetchone()
    if company_id is None:
        return None
    print('Company Id : ', company_id[0])
    return company_id[0]

def getLocationId(city,state,pin,lat,lng):
    city=city.lower()
    state=state.lower()
    country='canada'
    print('Location Id fetching funtion:',city,state,country)
    query='''select id from locations where city=%s and state=%s and country=%s and pin=%s and latitude=%s and longitude=%s '''
    cursor.execute(query,(city,state,country,pin,lat,lng))
    location_id = cursor.fetchone()
    if location_id is None:
        location_id =insertLocationIntoDb(city,state,pin,lat,lng,country)
    print('Location ID : ',location_id)
    return  location_id

def insertLocationIntoDb(city,state,pin,lat,lng,country):
    try:
        query= ''' INSERT INTO locations ( city, state,country,pin,latitude,longitude, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s ) RETURNING id; '''
        cursor.execute(query,(city,state,country,pin,lat,lng,str(datetime.datetime.now()),str(datetime.datetime.now())) )
        location_id = cursor.fetchone()[0]
        conn.commit()
        print('New Location created inserted successfully',location_id)
        return location_id
    except (Exception, psycopg2.Error) as error:
        print('Error in psql : ', error)

def checkErrorLogs():
    try:
        check = open("Error_Check.log", "r")
    except:
        return 'normal'
    lines = check.readlines()
    if len(lines) < 2:
        check.close()
        return 'normal'
    else:
        line = lines[-1]
        check.close()
        date = lines[0].split('\n')[0].strip()
        today = str(datetime.date.today())
        print(date, today)
        if date != today:
            print('Dates in error check are not matching.')
            return 'normal'
        return line

def make_new_log(filename):
    new = open(filename, "w")
    new.write(str(datetime.date.today()) + '\n')
    new.close()

def select_id_of_companies():
    query = f"select id,name from companies"
    cursor.execute(query)
    data = cursor.fetchall()
    print(len(data), 'No of jobs present in database.')
    return data

def insert_records_into_db(data):
    companies = list(data.keys())
    print('List of new companies : ',companies)
    company_data = []
    for company in companies:
        name = company.split('***')[0]
        city = company.split('***')[1]
        state_code = company.split('***')[2]
        fileName = company.split('***')[3]
        if fileName is 'None':
            fileName = ''
        if city != 'Remote' and state_code != 'Remote':
            state = stateFromStateCode(state_code)
            if city is 'None':
                city = ''
                pin = ''
                lat = 'NAN'
                lng = 'NAN'
            else:
                my_current_city_data = getPinLatLngFromCityFile(cities, city)
                pin = my_current_city_data[0]
                lat = my_current_city_data[1]
                lng = my_current_city_data[2]
                if pin is None or pin == '':
                    pin = ''
                    lat = 'NAN'
                    lng = 'NAN'
        else:
            city = ''
            state = ''
            pin = ''
            lat = 'NAN'
            lng = 'NAN'
        country = 'Canada'

        comp_id = getCompanyId(name)
        location_id = getLocationId(city,state,pin,lat,lng)

        print('Checked if company already exists', comp_id)
        print('Checked if Location Already exists:',location_id)
        if comp_id is None:
            temp_tuple = (name,str(datetime.datetime.now()),str(datetime.datetime.now()), fileName,location_id)
            company_data.append(temp_tuple)

    if len(company_data) > 0:
        insert_into_companies(company_data)
    original_id = []
    for item in data:
        name = item.split('***')[0]
        city = item.split('***')[1]
        state_code = item.split('***')[2]
        state = stateFromStateCode(state_code)
        if city is 'None':
            city = ''
            pin = ''
            lat = 'NAN'
            lng = 'NAN'
        else:
            my_current_city_data = getPinLatLngFromCityFile(cities, city)
            pin = my_current_city_data[0]
            lat = my_current_city_data[1]
            lng = my_current_city_data[2]
            if pin is None or pin == '':
                pin = ''
                lat = 'NAN'
                lng = 'NAN'
        company_id = getCompanyId(name)
        location_id = getLocationId(city,state,pin,lat,lng)

        jobs = []
        for i in data[item]:
            i[1] = company_id
            i.append(location_id)
            original_ids = checkJobIdsfromDB(i[6])
            if len(original_ids) > 0 or i[6] in original_id:
                summary.write('Duplicate entry found \n')
            else:
                original_id.append(i[6])
                jobs.append(i)

        if len(jobs) > 0:
            args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", tuple(x)).decode('utf-8') for x in jobs)
            cursor.execute("INSERT INTO jobs (title,company_id,remote, url,description, publish_date, uid, salary_range, job_types, created_at, updated_at,source_url,average_salary,location_id) VALUES " + args_str)
            conn.commit()


def insert_into_companies(data):
    try:
        args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s)", x).decode('utf-8') for x in data)
        cursor.execute("INSERT INTO companies (name, created_at, updated_at, image_link,location_id) VALUES " + args_str)
        conn.commit()
        print('New companies inserted successfully')
    except (Exception, psycopg2.Error) as error:
        print('Error in psql : ', error)

def get_cities_data():
    city_file = open('cities_data.csv','r', encoding='utf-8')
    cities_data = city_file.readlines()
    city_file.close()
    return cities_data

def identify_location(cities,location):
    if "," not in location:
        for item in state_short:
            if location.upper() == state_short[item].upper():
                return 'state'
        city = location.upper()
        print(city)
        for city_data in cities:
            city_data = city_data.split('\n')[0].split(',')
            if city in city_data[1]:
                return 'city'
        return 'continue'
    else:
        return 'city-state'

def getStateFromCityFile(cities, city):
    for city_data in cities:
        city_data = city_data.split(',')
        if city.upper() == city_data[1]:
            state_code = city_data[2]
            return state_code

def getPinLatLngFromCityFile(cities, city):
    for city_data in cities:
        city_data = city_data.split(',')
        if city.upper() == city_data[1]:
            pin = city_data[0]
            lat = city_data[4]
            lng = city_data[5]
            return [pin,lat,lng]
    return ['','','']

def stateFromStateCode(state_code):
    if state_code is not None:
        if state_code in state_short.keys():
            state = state_short[state_code]
            return state
        else:
            state = state_code
            return state
    else:
        state = ''
        return state

def close_desc_div(driver):
    try:
        driver.find_element_by_id('vjs-x').click()
        time.sleep(3)
        print('Closed job details div')
        return 'closed'
    except:
        checkPopOver(driver)
        checkCookieBox(driver)
        try:
            driver.find_element_by_id('vjs-x').click()
            time.sleep(3)
            print('Closed job details div')
            return 'closed'
        except (TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,NoSuchElementException) as e:
            if e is None or str(e) == '':
                e = 'Unknown Exception'
            return str(e)

def getDataFromNewTab(driver, company):
    try:
        button_txt = driver.find_element_by_xpath('//*[@id="applyButtonLinkContainer"]/div/div[2]/a').text
        if button_txt == 'Apply On Company Site' or 'Apply On Company Site' in button_txt:
            company_url = driver.find_element_by_xpath('//*[@id="applyButtonLinkContainer"]/div/div[2]/a').get_attribute('href')
            description = driver.find_element_by_id('jobDescriptionText').get_attribute('innerHTML')

            try:
                comp_div = driver.find_element_by_class_name('icl-Card-body')
                img_src = comp_div.find_element_by_xpath('.//a/img').get_attribute('src')
                print('Src : ', img_src)
                fileName = company + ".jpg"
                urllib.urlretrieve(img_src, 'logos/' + fileName)
            except:
                print('image src is not present')
                fileName = 'None'

            return  [company_url, description, fileName]
        else:
            return 'continue'
    except:
        # button_txt = driver.find_element_by_xpath('//*[@id="indeedApplyButtonContainer"]/span/div[2]/button/div').text
        return 'continue'

# # ***************  For developer use only  **************
chromedriver = "/usr/bin/chromedriver" #replace chromedriver path if not same with string
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)

 # ***************  For server use only  ****************

# driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', chrome_options=chrome_options)

summary = open('summary.log', 'w')
summary.write(str(datetime.date.today()) + '\n')
summary.close()

summary = open('summary.log', 'a')

origin_ids = []
cities = get_cities_data()
with_url = 0
without_url = 0
already_present = 0
data = {}
try:
    line = checkErrorLogs()
    make_new_log("Error_Check.log")
    log = open('Error_Check.log', 'a')
    for keyword in keywords:
        try:
            if line != 'normal':
                start_url = line.split(' ')[-1]
                status = line.split(' ')[1]
                if status == 'starting' and 'q='+keyword in start_url:
                    print('The script stopped on this url, so continuing from that.')
                    driver.get(start_url)
                    time.sleep(3)
                elif status == 'continuing' and 'q='+keyword in start_url:
                    print('The script stopped on this url, so continuing from that.')
                    driver.get(start_url)
                    time.sleep(3)
                elif status == 'success':
                    if keyword in start_url:
                        continue
                    print('Status is success, so going normally')
                    summary.write('There are no previous errors, so going normally' + '\n')
                    driver.get(f'https://ca.indeed.com/jobs?q={keyword}&fromage=14')
                    time.sleep(3)
                else:
                    continue
                line = 'normal'
            else:
                print('Going normally')
                summary.write('There are no previous errors, so going normally' + '\n')
                driver.get(f'https://ca.indeed.com/jobs?q={keyword}&fromage=1')
                time.sleep(3)
        except:
            print('Internet is not connected, or may be slow.')
            summary.write('Internet is not connected, or may be slow.' + '\n')

        log.write(keyword + ' starting ' + driver.current_url + '\n')
        summary.write(keyword + ' starting ' + driver.current_url + '\n')

        main_div = driver.find_element_by_id('resultsCol')
        stopper = False
        i=1
        while stopper == False:
            log.write(keyword + ' continuing ' + driver.current_url + '\n')
            summary.write(keyword + ' continuing ' + driver.current_url + '\n')
            checkPopOver(driver)
            try:
                job_divs = getJobsDiv(driver, 1)
                if job_divs == 'no_jobs':
                    summary.write('No jobs found in this keyword : '+ keyword + '\n')
                    break
            except:
                time.sleep(3)
                job_divs = getJobsDiv(driver,1)
            print('Starting scraping page '+ str(i) + ' : ' + str(datetime.datetime.now()))
            summary.write('Starting scraping page '+ str(i) + ' : ' + str(datetime.datetime.now()) + '\n')
            for job in job_divs:
                print('On new job now.')
                try:
                    origin_id = job.get_attribute('data-jk')
                    time.sleep(3)
                except:
                    continue
                original_ids = checkJobIdsfromDB(origin_id)
                if len(original_ids) > 0 or origin_id in origin_ids:
                    already_present += 1
                    print('This job is already present in database.')
                    summary.write(origin_id + ' -->  This job is already present in database.' + '\n')
                    continue
                else:
                    summary.write(origin_id + '  --> New job found' + '\n')
                    origin_ids.append(origin_id)

                try:
                    title = job.find_element_by_class_name('jobtitle').text
                except:
                    continue
                print('Title : ', title)
                try:
                    company = job.find_element_by_class_name('company').text
                    company = company.replace("'", "")
                except:
                    print('Company name in exception')
                    company = job.find_element_by_xpath('.//div[1]/div[1]/span').text
                    company = company.replace("'", "")
                print('Company : ', company)
                try:
                    location = job.find_element_by_class_name('location').text
                    if location == 'CANADA' or location == 'Canada':
                        city = 'None'
                        state = 'None'
                    else:
                        location_status = identify_location(cities, location)
                        print('Location Status : ', location_status)
                        if location_status == 'continue':
                            print(location, ' This location is not avaialabe.')
                            continue
                        elif location_status == 'city':
                            city = location
                            state = getStateFromCityFile(cities, city)
                            if state is None:
                                state = 'None'
                        elif location_status == 'state':
                            state = location
                            city = 'None'
                        elif location_status == 'city-state':
                            city = location.split(',')[0].strip()
                            state = location.split(',')[1].strip()
                    remote = False
                except:
                    location = job.find_element_by_class_name('remote').text
                    city = 'Remote'
                    state = 'Remote'
                    remote = True
                print('Location', location)
                print('Keyword :', keyword)

                summary.write('Title, Company, location is found...' + '\n')
                try:
                    salary_range = job.find_element_by_class_name('salaryText').text.strip()
                    if '-' in salary_range:
                        min_sal = salary_range.split('-')[0].replace(',','').strip()
                        max_sal = salary_range.split('-')[1].strip().split(' ')[0].replace(',','')
                        avg_salary = (int(min_sal[1:]) + int(max_sal[1:])) / 2
                        salary_range_sorted = '{'+min_sal+','+ max_sal+'}'
                        if 'hour' in salary_range:
                            job_type = '{Hourly}'
                            avg_salary = str(avg_salary * 8 * 5 * 52)
                        elif 'year' in salary_range:
                            job_type = '{Yealry}'
                        elif 'month' in salary_range:
                            job_type = '{Monthly}'
                            avg_salary = str(avg_salary * 12)
                    else:
                        salary_range = salary_range.split(' ')[0].replace(',', '')
                        salary_range_sorted = '{' + salary_range + '}'
                        avg_salary = int(salary_range_sorted[2:-1])
                        if 'hour' in salary_range:
                            job_type = '{Hourly}'
                            avg_salary = str(avg_salary * 8 * 5 * 52)
                        elif 'year' in salary_range:
                            job_type = '{Yealry}'
                        elif 'month' in salary_range:
                            job_type = '{Monthly}'
                            avg_salary = str(avg_salary * 12)
                        else:
                            job_type = '{Fixed}'
                    print('Salary Range : ', salary_range_sorted)
                    print('Job Type : ', job_type)
                    print('Average Salary : ', avg_salary)
                except:
                    print('Salary and job type is not provided')
                    salary_range_sorted = '{Not Provided}'
                    job_type = '{Not Provided}'
                    avg_salary = ''

                summary.write('Salary range and job type sections passed.' + '\n')

                try:
                    checkUrl1 = driver.current_url
                    job.click()
                    time.sleep(3)
                    summary.write('Clicked on job for further details' + '\n')
                except:
                    checkPopOver(driver)
                    time.sleep(1)
                    checkCookieBox(driver)
                    job.click()
                    time.sleep(3)
                    summary.write('Clicked on job for further details' + '\n')
                time.sleep(2.5)

                if len(driver.window_handles) > 1:
                    summary.write('There are more than one tabs opened' + '\n')
                    driver.switch_to.window(driver.window_handles[1])
                    my_newtab_data = getDataFromNewTab(driver, company)
                    time.sleep(2)
                    driver.close()
                    time.sleep(3)
                    driver.switch_to.window(driver.window_handles[0])
                    if type(my_newtab_data) is list:
                        company_url = my_newtab_data[0]
                        description = my_newtab_data[1]
                        fileName = my_newtab_data[2]
                        summary.write('Data found on new tab' + '\n')
                    else:
                        summary.write('Data cannot be found found on new tab' + '\n')
                        continue
                else:

                    job_url = driver.current_url

                    checkUrl2 = driver.current_url
                    if checkUrl1 == checkUrl2:
                        print('Job is not being clicked.')

                        continue

                    url = checkCompanyLink(driver, job, 1)
                    if url != 'continue':
                        company_url = url
                        with_url += 1
                        print(with_url, 'With url')
                        print('Url :', company_url)
                    else:
                        print('No company website available.')
                        summary.write('No url found related to employer company.' + '\n')
                        without_url += 1
                        summary.write('Closing job details div' + '\n')
                        print('Closing job details div')
                        close_desc_div(driver)
                        summary.write('Closed job details div' + '\n')
                        print('Closed job details div')
                        continue

                    try:
                        logo_div = driver.find_element_by_class_name('vjs-JobInfoHeader-logo-container')
                        logo_src = logo_div.find_element_by_tag_name('img').get_attribute('src')
                        print('Logo Source :', logo_src)
                        fileName = company + ".jpg"
                        urllib.urlretrieve(logo_src, 'logos/' + fileName)
                    except:
                        try:
                            logo_src = driver.find_element_by_id('vjs-img-cmL').get_attribute('src')
                            print('Logo Source :', logo_src)
                            fileName = company + ".jpg"
                            urllib.urlretrieve(logo_src, 'logos/' + fileName)
                        except:
                            fileName = 'None'
                    try:
                        description = driver.find_element_by_id('vjs-desc').get_attribute('innerHTML')
                        print('Description found ')
                    except:
                        time.sleep(2.5)
                        description = driver.find_element_by_id('vjs-desc').get_attribute('innerHTML')
                        print('Description found in exception')

                    summary.write('Description found for the job.' + '\n')

                    summary.write('Closing job details div' + '\n')
                    print('Closing job details div')
                    close_desc_div(driver)
                    summary.write('Closed job details div' + '\n')
                    print('Closed job details div')

                today = str(datetime.date.today())
                created_at = str(datetime.datetime.now())
                company_id = ''
                job_data = [title,company_id,remote, company_url, description, today, origin_id, salary_range_sorted, job_type, created_at, created_at, job_url, avg_salary]

                company_key = company+'***'+city+'***'+state+'***'+fileName
                print('Company Key : ', company_key)
                if company_key in data.keys():
                    data[company+'***'+city+'***'+state+'***'+fileName].append(job_data)
                else:
                    data[company+'***'+city+'***'+state+'***'+fileName] = [job_data]

                print('End one job')

            try:
                checkWindowHandles(driver)
                checkCookieBox(driver)
                print('Ending page scraping : ' + str(i) + str(datetime.datetime.now()))
                summary.write('Ending page scraping : ' + str(i) + str(datetime.datetime.now()) + '\n')
                pagination = driver.find_element_by_class_name('pagination')
                links = pagination.find_elements_by_tag_name('a')
                print(len(links), 'Num of links in pagination')

                try:
                    text = links[len(links)-1].text
                    if text == '':
                        text = links[len(links) - 1].get_attribute('aria-label')
                    print(text, 'pagination text')
                    if 'Next' in text:
                        i+=1
                        checkBeforeUrl = driver.current_url
                        if '&start' in checkBeforeUrl:
                            if '&vjk=' in checkBeforeUrl:
                                checkBeforeUrl = checkBeforeUrl.split('&vjk=')[0]
                            if '&advn=' in checkBeforeUrl:
                                checkBeforeUrl = checkBeforeUrl.split('&advn=')[0]
                            checkBeforeUrl = int(checkBeforeUrl.split('&start=')[-1])
                        else:
                            checkBeforeUrl = 0
                        links[len(links)-1].click()
                        time.sleep(3)
                        summary.write('Clicked on next button.' + '\n')
                        time.sleep(2)
                        checkAfterUrl = driver.current_url
                        checkAfterUrl = int(checkAfterUrl.split('=')[-1])
                        if checkBeforeUrl > checkAfterUrl:
                            stopper = True
                    else:
                        print('Setting stopper to true because next button is not found')
                        summary.write('Setting stopper to true because next button is not found' + '\n')
                        stopper = True
                except:
                    stopper = True
            except:
                print('No pages are there.')
                summary.write('No pages are there.' + '\n')
                break
        log.write(keyword + ' success' + ' ' + driver.current_url + '\n')
        summary.write(keyword + ' success' + ' ' + driver.current_url + '\n')

    summary.write('Inserting records into database....' + '\n')
    insert_records_into_db(data)
    summary.write(str(datetime.datetime.now())+  ' Ending script time' + '\n')
    summary.write('Script has come to an end.' + '\n')
    summary.close()
    msg = f"""Scraping script has been completed.
              <br/> Total Jobs checked : {with_url + without_url}
              <br/> Records Fetched : {with_url}
              <br/> Duplicate Records found : {already_present}"""
    send_mail('azadveer.hakuwala@gmail.com', 'Indeed Scraper Daily: Success', msg)

except (TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,NoSuchElementException) as exception:
    # insert fetched records in database.
    if exception is None or exception == '':
        exception = 'Unknown exception'
    summary.write('Exception in script'+ str(exception) + '\n')
    insert_records_into_db(data)
    msg = f"""Please rerun the script to continue scraping.
              <br/> Total Jobs checked : {with_url + without_url}
              <br/> jobs Fetched : {with_url}
              <br/> Duplicate Records found : {already_present}"""
    summary.write(str(datetime.datetime.now())+  ' Ending script time' + '\n')
    summary.write('Script has come to an end.' + '\n')
    summary.close()
    send_mail('azadveer.hakuwala@gmail.com', 'Indeed Scraper Daily: Error', msg)
except:
    summary.write('Inside exception 2' + '\n')
    insert_records_into_db(data)
    msg = f"""Please rerun the script to continue scraping.
              <br/> Total Jobs checked : {with_url + without_url}
              <br/> Records Fetched : {with_url}
              <br/> Duplicate Records found : {already_present}"""
    summary.write(str(datetime.datetime.now())+  ' Ending script time' + '\n')
    summary.write('Script has come to an end.' + '\n')
    summary.close()
    send_mail('azadveer.hakuwala@gmail.com', 'Indeed Scraper Custom: Error',msg)

finally:
    log.close()
    driver.quit()

