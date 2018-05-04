from flask import Flask, render_template, request, Markup
import sqlite3
from datetime import datetime
from dateutil import parser

# from flask_bootstrap import Bootstrap
app = Flask(__name__)
# Bootstrap(app)

Database = 'Attendance.db3'


def connect():
    return sqlite3.connect(Database)


@app.route('/')
def Reg_class():
    return render_template('Reg_Class.html')


# @app.route('/Reg_Class')
# def Reg_class():
#     return render_template('Reg_Class.html')


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
    ulid = request.form['ulid']
    crse_id = request.form['crse_id']
    if stu_name == "" or ulid == "" or crse_id == "":
        return render_template('Reg_Students.html', valid=False, option_list=opt_list)
    else:
        db.execute('Insert into Registration_Details values (?,?)', (ulid, crse_id))
        db.commit()
        db.close()
        return render_template('Reg_Students.html', valid=True, option_list=opt_list)


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
        db.execute('Insert into Class_Schedule values (?,?,?,?,?)', (crse_id, crse_name, Day, Strt_time, End_time))
        db.commit()
        return render_template('Reg_Class.html', valid=True)


@app.route('/Stats')
def stats():
    db = connect()
    cur = db.cursor()
    cur1 = db.cursor()
    cur.execute('Select Course_id from Class_Schedule')
    opt_list = [dict(Course_id=row[0]) for row in cur.fetchall()]
    cur1.execute('Select * from Attendance')
    atn_list = [dict(ULID=row[1], TimeStamp=row[2]) for row in cur1.fetchall()]
    return render_template('Stats.html', option_list=opt_list)


@app.route('/stats', methods=['Post'])
def Show_Stats():
    course_id = request.form['crse_id']
    db = connect()
    cur = db.cursor()
    cur1 = db.cursor()
    cur2 = db.cursor()
    cur3 = db.cursor()

    cur.execute('Select Course_id from Class_Schedule')
    opt_list = [dict(Course_id=row[0]) for row in cur.fetchall()]

    cur1.execute('Select * from Registration_Details where Course_id = ?', (course_id,))
    reg_list = [dict(ULID=row[0], Course_id=row[1]) for row in cur1.fetchall()]

    cur2.execute('Select ULID, TimeStamp from Attendance where Course_id = ?', (course_id,))
    atn_list = [dict(ULID=row[0], TimeStamp=row[1]) for row in cur2.fetchall()]

    cur3.execute('select rd.ulid, count(a.ULID) as total from registration_details rd LEFT JOIN Attendance a '
                 'on rd.Course_id = a.Course_id and rd.ulid= a.ULID '
                 'where rd.Course_id = ? GROUP by rd.ULID', (course_id,))
    tot_list = [dict(ULID=row[0], total=row[1]) for row in cur3.fetchall()]

    return render_template('Stats.html', reg_list=reg_list, atn_list=atn_list, tot_list=tot_list,
                           option_list=opt_list)


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


@app.route('/graph', methods = ['Post'])
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

    return render_template('Graph.html', values=count_list, labels=month_list, option_list=opt_list, canvas = True)


if __name__ == '__main__':
    app.run(debug=True)
