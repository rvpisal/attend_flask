from flask import Flask, render_template, request, Markup
import sqlite3
from datetime import datetime
from dateutil import parser

# from flask_bootstrap import Bootstrap
app = Flask(__name__)
# Bootstrap(app)

Database = "../web/Attendance.db3"

# CREATE TABLE "Attendance" (`Course_id` TEXT,`ULID`	TEXT,`TimeStamp`	TEXT,`Day`	TEXT,
# 	PRIMARY KEY(`Course_id`,`TimeStamp`,`ULID`)
# )
#
# CREATE TABLE "Class_Schedule" (	`Course_id`	TEXT,`Subject_name`	text,`Day`	Text,`Start_Time`	date,
# 	`End_Time`	date,PRIMARY KEY(`Course_id`,`Day`))
# #
# CREATE TABLE "Registration_Details" (	`ULID`	TEXT,	`Student_Name`	TEXT,	`Course_id`	INTEGER,	PRIMARY KEY(`ULID`,`Course_id`))


def connect():
    with sqlite3.connect(Database) as db:
        db.execute("CREATE TABLE IF NOT EXISTS Attendance (Course_id TEXT,ULID TEXT,TimeStamp	TEXT,Day TEXT, "
               "PRIMARY KEY(Course_id,TimeStamp, ULID))")
        db.execute("CREATE TABLE IF NOT EXISTS Class_Schedule (Course_id TEXT,Subject_name text, Day Text,"
                   "Start_Time	date,End_Time date,PRIMARY KEY(Course_id,Day))")
        db.execute("CREATE TABLE IF NOT EXISTS Registration_Details (ULID	TEXT,Student_Name TEXT,Course_id INTEGER"
                   ",PRIMARY KEY(ULID,Course_id))")

    return sqlite3.connect(Database)


@app.route('/')
def Home():
    return render_template('HomePage.html')

@app.route('/Reg_Class')
def Reg_class():
    return render_template('Reg_Class.html')


@app.route('/Ins_Crse', methods=['Post'])
def Ins_Crse():
    crse_id = request.form['crse_id']
    crse_name = request.form['crse_name']
    Day = request.form['day']
    Strt_time = request.form['strt_time']
    End_time = request.form['end_time']
    if crse_id == "" or crse_name == "" or Day == "" or Strt_time == "" or End_time == "":
        return render_template('Reg_Class.html', valid=False)
    else:
        db = connect()
        try:
            db.execute('Insert into Class_Schedule values (?,?,?,?,?)', (crse_id, crse_name, Day, Strt_time, End_time))
            db.commit()
            return render_template('Reg_Class.html', valid=True)
        except sqlite3.IntegrityError as e:
            return render_template('Reg_Class.html', err=True)


@app.route('/Reg_Students')
def Reg_stu():
    db = connect()
    cur = db.cursor()
    cur.execute('Select Course_id from Class_Schedule')
    opt_list = [dict(Course_id=row[0]) for row in cur.fetchall()]
    cur.close()
    db.close()
    return render_template('Reg_Students.html', option_list=opt_list)


@app.route('/Ins_stu', methods=['Post'])
def Ins_stu():
    db = connect()
    cur = db.cursor()
    cur.execute('Select Course_id from Class_Schedule')
    opt_list = [dict(Course_id=row[0]) for row in cur.fetchall()]

    stu_name = request.form['stu_name']
    ulid = str(request.form['ulid']).lower()
    crse_id = request.form['crse_id']
    if stu_name == "" or ulid == "" or crse_id == "":
        return render_template('Reg_Students.html', valid=False, option_list=opt_list)
    else:
        try:
            db.execute('Insert into Registration_Details values (?,?,?)', (ulid, stu_name, crse_id))
            db.commit()
            db.close()
            return render_template('Reg_Students.html', valid=True, option_list=opt_list)
        except sqlite3.IntegrityError as e:
            return render_template('Reg_Students.html', err=True, option_list=opt_list)


@app.route('/Stats')
def stats():
    db = connect()
    cur = db.cursor()


    cur.execute('Select Course_id from Class_Schedule')
    opt_list = [dict(Course_id=row[0]) for row in cur.fetchall()]

    return render_template('Stats.html',  option_list=opt_list)


@app.route('/stats', methods=['Post'])
def Show_Stats():
    course_id = request.form['crse_id']
    db = connect()
    cur = db.cursor()
    cur1 = db.cursor()
    cur2 = db.cursor()
    cur3 = db.cursor()
    cur4 = db.cursor()

    cur.execute('Select Course_id from Class_Schedule')
    opt_list = [dict(Course_id=row[0]) for row in cur.fetchall()]

    cur1.execute('Select ULID, TimeStamp from Attendance where Course_id = ?', (course_id,))
    atn_list = [dict(ULID=row[0], TimeStamp=row[1]) for row in cur1.fetchall()]

    cur2.execute('select rd.ulid, count(a.ULID) as total from registration_details rd LEFT JOIN Attendance a '
                 'on rd.Course_id = a.Course_id and rd.ulid= a.ULID '
                 'where rd.Course_id = ? GROUP by rd.ULID', (course_id,))
    tot_list = [dict(ULID=row[0], total=row[1]) for row in cur2.fetchall()]

    cur3.execute('Select Distinct Course_id,Subject_name from Class_Schedule where Course_id = ?',(course_id,))
    course_det = list([str(row[0]) for row in cur3.fetchall()])

    print(course_det)

    crse_det = course_det[0]



    print(crse_det)

    return render_template('Stats.html', atn_list=atn_list, tot_list=tot_list,
                           option_list=opt_list,show_tab=True, course_details = crse_det)


@app.route('/tp')
def chart():
    labels = [50, "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('tp.html', values=values, labels=labels)
    # return render_template('tp.html')


@app.route('/Graph')
def Graph():
    db = connect()
    cur = db.cursor()
    cur.execute('Select Course_id from Class_Schedule')
    opt_list = [dict(Course_id=row[0]) for row in cur.fetchall()]
    return render_template('Graph.html', option_list=opt_list)


@app.route('/graph', methods=['Post'])
def graph_main():
    db = connect()
    cur = db.cursor()
    cur1 = db.cursor()
    Crse_id = request.form['crse_id']
    month_list = []
    count_list = []

    cur1.execute('Select Course_id from Class_Schedule')
    opt_list = [dict(Course_id=row[0]) for row in cur1.fetchall()]

    cur.execute('select date(TimeStamp),count(*) from Attendance where Course_id = ?'
                ' GROUP by date(TimeStamp)', (Crse_id,))

    for row in cur.fetchall():
        # print(i)
        date = datetime.strptime(row[0], '%Y-%m-%d')
        str_date = date.strftime("%B") + '-' + date.strftime("%d")
        month_list.append(str_date)
        count_list.append(row[1])

    return render_template('Graph.html', values=count_list, labels=month_list, option_list=opt_list, canvas=True)


if __name__ == '__main__':
    app.run(debug=True)
