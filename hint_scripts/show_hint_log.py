# Log the time student click the 'show_hint' button
import os
import sys
import MySQLdb
from flask import request, Flask
from flask_cors import CORS, cross_origin

import logging.handlers
import logging
# logging settings
log_path = '/home/zzhai/hint_log/show_hint.log'
logger = logging.getLogger('show_hint')
handler = logging.handlers.RotatingFileHandler(log_path, maxBytes = 262144, backupCount = 16)
formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


db = MySQLdb.connect("localhost","root","","ucsd_cse103" )
db_cursor = db.cursor()

'''Create the table, should be executed only once'''
create_show_hint_click_table_sql = """CREATE TABLE show_hint_click(
                                        id int NOT NULL AUTO_INCREMENT,
                                        problem_name CHAR(255),
                                        problem_part CHAR(255), 
                                        student_username CHAR(255),
                                        time_clicked TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                                        PRIMARY KEY (ID) )"""

#db_cursor.execute(create_show_hint_click_table_sql)  

'''Create the table, should be executed only once'''
create_hint_log_table_sql = """CREATE TABLE hint_log(
                                        id int NOT NULL AUTO_INCREMENT,
                                        problem_name CHAR(255),
                                        problem_part CHAR(255), 
                                        student_username CHAR(255),
                                        hint_content CHAR(255),
                                        attempt CHAR(255),
                                        time_clicked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        PRIMARY KEY (ID) )"""                   

#db_cursor.execute(create_hint_log_table_sql)

app = Flask(__name__)
CORS(app)

@app.route('/show_hint_button_clicked', methods=['POST'])
def index():
    logger.info("captured post")
    student_username = request.form["student_name"]
    problem_info = request.form["problem_info"]
    hint_content = request.form["hint"]
    attempt = request.form['attempt']
    logger.info("grabbed input:")
    logger.info("\t student_name {0}, problem_info {1}, hint_content {2}, attempt {3}.".format(student_username, problem_info, hint_content, attempt))
    try:
        week_pos, problem_pos, part_pos = \
             problem_info.find('week'), problem_info.find('problem'), problem_info.find('part')
        week_id, problem_id, part_id = \
                 problem_info[week_pos+4:problem_pos], problem_info[problem_pos+7:part_pos], problem_info[part_pos+4:]
        problem_name = "Week{0}_Problem{1}".format(week_id, problem_id)
        problem_part = part_id
        new_record = (problem_name, problem_part, student_username, hint_content, attempt)
    except:
        logger.error("problem_info format wrong: {0}".format(problem_info))
        return "problem_info format wrong: {0}".format(problem_info) 
    
    try:
        insert_sql = """INSERT INTO hint_log (problem_name, problem_part, student_username, hint_content, attempt)
                        VALUES(%s,%s,%s,%s,%s)"""  
        db_cursor.execute(insert_sql,new_record)
        db.commit()
    except:
        db.rollback()
        logger.error("Exception {0}".format(traceback.format_exc()))
        return "Database has been rolled back because of an Exception !!!{0}".format(traceback.format_exc())  
    # db.close()
    
    logger.info("return success")
    return 'success'

app.run(host='0.0.0.0')