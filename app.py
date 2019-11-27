from flask import Flask, render_template, request, redirect,session
from flask_mysqldb import MySQL
import yaml
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
# config db
db = yaml.load(open('user.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def home():

	return render_template('homepage.html')

@app.route('/register')
def register():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM district")
	dist = cur.fetchall()
	return render_template('register.html',dist=dist)

@app.route('/register1', methods=['GET', 'POST'])
def register1():

	if request.method == 'POST':
	#fetch form data
		userDetails = request.form
		hname = userDetails['hname']
		mobile = userDetails['mobile']
		lmobile = userDetails['lmobile']
		email = userDetails['email']
		district = userDetails['district']
		city = userDetails['city']
		pincode = userDetails['pin']
		password = userDetails['password']
		status=0
		role=1
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO login(email,password,role)values(%s,%s,%s)",(email,password,role))
		mysql.connection.commit()
		cur.execute("SELECT lid FROM login WHERE email = '" + email + "' and password = '" + password + "'")
		data = cur.fetchone()
		lid = data[0]
		cur.execute("INSERT INTO hsptl(lid ,name, contact, lan, email, dist, city, pincode ,status)VALUES(%s, %s, %s, %s, %s, %s, %s, %s ,%s)",(lid,hname,mobile,lmobile,email,district,city,pincode,status))
		mysql.connection.commit()
		cur.close()
		return render_template('login.html')
	return redirect('register')

@app.route('/login', methods=['GET', 'POST'])
def login():

	cursor = mysql.connection.cursor()
	if request.method == 'POST':
		email=request.form['email']
		password=request.form['password']
        	cursor.execute("SELECT * FROM login WHERE email = '" + email + "' and password = '" + password + "'")
        	data = cursor.fetchone()
		if data is None:
			return render_template('login.html',val=1)
		else:
			role = data[3]
			if role == 0:
				session['email'] = data[1]
				return redirect('/adminhome')
			elif role ==1:
				cursor.execute("SELECT * FROM hsptl WHERE email = '" + email + "' and status = 1")
				data1 = cursor.fetchone()
				if data1 is None:
					return render_template('login.html',val=2)
				else:
					session['email'] = data1[5]
					session['hid'] = data1[0]
					return redirect('/userhome')
		cursor.close()
	return render_template('login.html')
@app.route('/userhome')
def userhome():

	if 'email' in session :
		return render_template('userhome.html')
	else :
		return redirect('login')

@app.route('/adminhome')
def adminhome():
	if 'email' in session :
		return render_template('adminhome.html')
	else :
		return redirect('login')

@app.route('/hospitals')
def hospitals():

	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM hsptl where status = 1")
	hsptl = cur.fetchall()
	return render_template('hospitals.html',hsptl=hsptl)

@app.route('/district', methods=['GET', 'POST'])
def district():
    if request.method == 'POST':
        userDetails = request.form
        dname = userDetails['dname']
        status = 1
        cur = mysql.connection.cursor()
	cur.execute("INSERT INTO district(dname,status)values(%s,%s)",(dname,status))
	mysql.connection.commit()
        
    return render_template('district.html')

@app.route('/patient_registration')
def patient_registration():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM district")
	dist = cur.fetchall()
	return render_template('patient.html',dist=dist)

@app.route('/patient', methods=['GET', 'POST'])
def patient():

	if request.method == 'POST':
	#fetch form data
		userDetails = request.form
		hid = session['hid']
		pname = userDetails['name']
		lname = userDetails['lname']
		address = userDetails['address']
		mobile = userDetails['mobile']
		dist = userDetails['district']
		city = userDetails['city']
		age = userDetails['age']
		sex = userDetails['sex']
		pincode = userDetails['pin']
		dise = userDetails['dicease']
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO patient(hid ,pname ,lname ,address ,mobile ,dist ,city ,age ,sex ,pin,dise)VALUES(%s, %s, %s, %s, %s, %s, %s, %s ,%s,%s,%s)",(hid,pname,lname,address,mobile,dist,city,age,sex,pincode,dise))
		mysql.connection.commit()
		cur.close()
		return redirect('details')
	return redirect('patient_registration')

@app.route('/contactus')
def contactus():

	return render_template('contactus.html')

@app.route('/aboutas')
def aboutas():
	return render_template('about.html')

@app.route('/details')
def details():

	hid = session['hid']
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM patient where hid = hid ")
	pati = cur.fetchall()
	return render_template('details.html',pati=pati)

@app.route('/delete', methods=["GET","POST"])
def delete():

	cur = mysql.connection.cursor()
	if request.method == 'POST':
	#fetch form data		
		hid = request.form['hid1']
		cur.execute("UPDATE hsptl SET status=0 WHERE hid = '" + hid + "'")
		mysql.connection.commit()
		cur.close()
	return redirect('hospitals')

@app.route('/approve', methods=["GET","POST"])
def approve():

	cur = mysql.connection.cursor()
	if request.method == 'POST':
	#fetch form data
		hid = request.form['hid1']
		cur.execute("UPDATE hsptl SET status=1 WHERE hid = '" + hid + "'")
		mysql.connection.commit()
		cur.close()
		return redirect('notification')

@app.route('/notification')
def notification():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM hsptl where status = 0")
	hsptl = cur.fetchall() 
	return render_template('notification.html',hsptl=hsptl)

@app.route('/change_password', methods=["GET","POST"])
def change_password():

	cur = mysql.connection.cursor()	
	if request.method == 'POST':
		email = session['email']
		psw=request.form['password']
		cpsw=request.form['cpassword']
		if psw == cpsw :
			cur.execute("UPDATE login SET password = '" + psw + "' WHERE email = '" + email + "'")
			mysql.connection.commit()
			cur.close()
			return render_template('adminhome.html')
		else:
			return render_template('adminpass.html',val=1)
	return render_template('adminpass.html')

@app.route('/change_password_h', methods=["GET","POST"])
def change_password_h():

	cur = mysql.connection.cursor()	
	if request.method == 'POST':
		email = session['email']
		psw=request.form['password']
		cpsw=request.form['cpassword']
		if psw == cpsw :
			cur.execute("UPDATE login SET password = '" + psw + "' WHERE email = '" + email + "'")
			mysql.connection.commit()
			cur.close()
			return render_template('userhome.html')
		else:
			return render_template('password.html',val=1)
	return render_template('password.html')

@app.route('/logout')
def logout():
	session.pop('email', None)
	session.pop('hid', None)
	return redirect('login')

if __name__ == '__main__':
     app.run(debug=True)
