from flask import Flask,render_template, request
import sqlite3
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



@app.route('/Ins_stu', methods = ['Post'])
def Ins_stu():
    db = connect()
    cur = db.cursor()
    cur.execute('Select Course_id from Class_Schedule')
    opt_list = [dict(Course_id=row[0]) for row in cur.fetchall()]

    stu_name = request.form['stu_name']
    ulid = request.form['ulid']
    crse_id = request.form['crse_id']
    if stu_name == "" or ulid == "" or crse_id == "":
        return render_template('Reg_Students.html',valid=False, option_list=opt_list)
    else:
        db.execute('Insert into Registration_Details values (?,?)',(ulid,crse_id))
        db.commit()
        db.close()
        return render_template('Reg_Students.html', valid=True, option_list=opt_list)


@app.route('/Ins_Crse', methods = ['Post'])
def Ins_Crse():
    crse_id = request.form['crse_id']
    crse_name = request.form['crse_name']
    Day = request.form['day']
    Strt_time = request.form['strt_time']
    End_time = request.form['end_time']
    if crse_id == "" or crse_name == "" or Day == "" or Strt_time == "" or End_time == "":
        return render_template('Reg_Class.html',valid=False)
    else:
        db = connect()
        db.execute('Insert into Class_Schedule values (?,?,?,?,?)',(crse_id,crse_name,Day,Strt_time,End_time))
        db.commit()
        return render_template('Reg_Class.html', valid=True)

@app.route('/Stats')
def stats():
    return  render_template('Stats.html')


if __name__ == '__main__':
    app.run(debug=True)
