from hashlib import pbkdf2_hmac
from getpass import*
from account_manager import*
from supervisor import*
from dispatcher import*
from driver import*
import sqlite3
import re


connection = None
cursor = None

def main():
	global connection, cursor

	path="./waste_management.db"
	connect(path)
	welcome_screen()
	connection.commit()

def connect(path):
	global connection, cursor

	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute('PRAGMA foreign_keys=ON; ')

	connection.commit()

def welcome_screen():
	global connection,cursor

	while(1):

		status=input("Do you want to sign up(s), log in(l), or quit(q)? ")
		
		if status == "q" or status == "Q":
			break

		elif status == "l" or status == "L":
			log_in()
			break

		elif status == "s" or status == "S":
			sign_up()
			break

		else:
			print("Invalid command, please enter again")
			continue
					
	connection.commit()

#ask user to log in the system
def log_in():

	exit=0
	exit1=0
	while(exit < 3 and exit1 <3):
		username=input("Please input your username ")
		if check_username(username) is not False:
			username=check_username(username)
			pwd=getpass(prompt="Please input your password: ")
			if check_password(username,pwd) is True:
				 cursor.execute("select role from users where login=:username",{"username":username})
				 role=cursor.fetchone()
				 role=role[0]
				 cursor.execute("select user_id from users where login=:username",{"username":username})
				 user_id=cursor.fetchone()
				 user_id=user_id[0]
				 if re.match(role,"account manager",re.IGNORECASE) != None:
				 	 account_manager(user_id,connection,cursor)
				 	 break
				 if re.match(role,"supervisor",re.IGNORECASE) != None:
				 	 supervisor(user_id,connection,cursor)
				 	 break
				 if re.match(role,"dispatcher",re.IGNORECASE) != None:
				 	 dispatcher(user_id,connection,cursor)
				 	 break
				 if re.match(role,"driver",re.IGNORECASE) != None:
				 	 driver(user_id,connection,cursor)
				 	 break
			else:
				
				exit1+=1
				if exit1 < 3:
					print("The username or password entered is not correct, please input again")
				continue
		else:

			exit+=1

			if exit < 3:
				print("The username inputed does not exist, please input again ")
			continue

	if exit == 3 or exit1  == 3:
		print("Your have login failed 3 times, the system has been shutdown")

#ask user to sign up a new account
def sign_up():

	global connection,cursor

	hash_name='sha256'
	salt='ssdirf9931ksiqb4'
	iterations = 100000

	user_id=str(input("Please enter your user id: "))
	while(check_pid(user_id) is False or check_exist_pid(user_id) is True):
		if check_pid(user_id) is False:
			print("This user id does not exist, please enter again")
		else:
			print("The user_id entered is existed, please log in directly or create another user")
			welcome_screen()

		user_id=str(input("Please enter your user id: "))

	role=str(input("Please enter your role: "))

	while(check_role(user_id,role) is False):
		print("The role entered is not matched, please enter again")
		role=str(input("Please enter your role: "))

	login=str(input("Please enter your username: "))
	while(check_username(login) is not False):
		print("This username has been occupied, please select another username")
		login=str(input("Please enter your username: "))

	password=str(input("Pleaes enter your password: "))

	pwd=pbkdf2_hmac(hash_name,bytearray(password,'ascii'),bytearray(salt,'ascii'),iterations)

	insert_user="INSERT INTO users VALUES(:user_id,:role,:login,:password)"
	cursor.execute(insert_user,{"user_id":user_id,"role":role.lower(),"login":login.lower(),"password":pwd})
	connection.commit()
	welcome_screen()

#check if the pid is in the database
def check_pid(pid):
	global connection,cursor

	cursor.execute("select pid from personnel")

	result=cursor.fetchall()

	pid_list=[]

	for i in result:
		pid_list.append(i[0])

	if pid in pid_list:

		return True

	else:

		return False

#given a user_id,check if it is already in the user table
def check_exist_pid(user_id):

	cursor.execute("SELECT user_id from users")
	result=cursor.fetchall()

	user_ids=[]

	for i in result:
		user_ids.append(i[0])

	if user_id in user_ids:
		return True
	else:
		return False

#check if the user_id entered is matched with the role entered
def check_role(user_id,role):
	global connection,cursor

	cursor.execute("select pid from account_managers")
	result=cursor.fetchall()
	manager_list=[]
	for i in result:
		manager_list.append(i[0])

	cursor.execute("select pid from drivers")
	result=cursor.fetchall()
	driver_list=[]
	for i in result:
		driver_list.append(i[0])

	cursor.execute("select supervisor_pid from personnel where pid=:user_id",{"user_id":user_id})
	result=cursor.fetchall()
	supervisor_list=[]
	for i in result:
		supervisor_list.append(i[0])

	if user_id in manager_list and re.match(role,"account manager",re.IGNORECASE) != None:
		return True

	elif user_id in driver_list and re.match(role,"driver",re.IGNORECASE) != None:
		return True

	elif user_id in supervisor_list and re.match(role,"supervisor",re.IGNORECASE) != None:
		return True

	elif re.match(role,"dispatcher",re.IGNORECASE) != None:
		return True

	else:
		return False

#check if the username has already existed
def check_username(username):

	global connection,cursor

	cursor.execute("select login from users;")
	username_list=cursor.fetchall()
	name_list=[]
	lower_list=[]
	index=-1

	test_name=username.lower()

	for i in username_list:
		lower_list.append(i[0].lower())
		name_list.append(i[0])

	for i in range(len(lower_list)):

		if lower_list[i] == test_name:
			index = i

	if index != -1:
		return name_list[index]
	else:
		return False

#check if the password matched
def check_password(username,password):

	global connection,cursor

	hash_name='sha256'
	salt='ssdirf9931ksiqb4'
	iterations = 100000

	dk2=pbkdf2_hmac(hash_name,bytearray(password,'ascii'),bytearray(salt,'ascii'),iterations)
	cursor.execute("select password from users where login=:username",{"username":username})

	pwd=cursor.fetchone()
	pwd=pwd[0]
	if dk2 == pwd:
		return True
	else:
		return False

main()
