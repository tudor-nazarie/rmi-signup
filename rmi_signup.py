#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from flask import Flask, render_template, request
import requests
import psycopg2
from subprocess import call

app = Flask(__name__)

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
site_key = "6LcKZwoUAAAAANjLrUp-ED7tqHAMHiKt7G5ZUMtK"
secret_key = "6LcKZwoUAAAAAEaGWrGgZvNAt-Xxjn1RR6x0Hkh4"


def verify_captcha(response=None, remote_ip=None):
	data = {
		"secret": secret_key,
		"response": response,
		"remoteip": remote_ip
	}
	r = requests.get(VERIFY_URL, params=data)
	return r.json()["success"] if r.status_code == 200 else False

@app.route('/', methods=['POST', 'GET'])
def register():
	error = None
	registered = False
	username = None
	if request.method == 'POST':
		first_name = request.form['fname']
		last_name = request.form['lname']
		# username = request.form['username']
		school = request.form['school']
		email = request.form['email']
		password = request.form['password']
		confirm = request.form['confirm']
		username = "{0}.{1}.{2}".format(first_name, last_name, school)

		re_response = request.form['g-recaptcha-response']
		if verify_captcha(response=re_response):
			if password == confirm:
				conn = psycopg2.connect(database="cmsdb", user="cmsuser", password="Cmsuser42;8")
				cur = conn.cursor()
				cur.execute("SELECT * FROM \"users\" WHERE username = '{0}'".format(username))
				if cur.fetchone() is None:
					call(["/home/xdizzaster/rmi/bin/cmsAddUser", "-p", password, "-e", email, first_name, last_name,
					      username])
					call(["/home/xdizzaster/rmi/bin/cmsAddParticipation", "-c", "2",
					      username])  # maaan, this hack dirty as fuck
					# return redirect("http://lbi.ro")
					registered = True
				else:
					error = "Te poţi înregistra doar o singură dată."
			else:
				error = "Parolele trebuie să fie identice."
		else:
			error = "Va rugam demonstrati ca sunteti om."
	return render_template('index.html', error=error, registered=registered, username=username)


if __name__ == "__main__":
	app.run(host="0.0.0.0")
