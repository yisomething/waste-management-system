import sqlite3
import re
from account_manager import*
global connection, cursor

def supervisor(pid,connection,cursor):
	

	print("What function do you want to use? ")
	print("1: Assign a new account to a manager ")
	print("2: Create a summary report for a customer")
	print("3: Create a summary report for account managers")
	print("4: Log out")

	while(1):
		try:
			choice=int(input("Enter your choice: "))
		except:
			print("Invalid command,please select again")
			continue
		if choice == 1:
			assign_account(pid,connection,cursor)
			break			

		elif choice == 2:
			customer_report(pid,connection,cursor)
			break

		elif choice == 3:
			manager_report(pid,connection,cursor)
			break

		elif choice == 4:
			break

		else:
			print("Invalid command,please select again")
			continue

	connection.commit()

#to check if this supervisor supervise this account,manager
def check_manager(pid,manager,connection,cursor):

	cursor.execute("select pid from personnel where supervisor_pid=:pid",{"pid":pid})
	result=cursor.fetchall()

	pid_list=[]

	for i in result:
		pid_list.append(i[0])

	if manager in pid_list:
		return True

	else:
		return False

#to check if this customer managed by an account manager who supervised by this supervisor
def check_customer(supervisor_id,master_account,connection,cursor):

	cursor.execute("select account_mgr from accounts where account_no=:master_account",{"master_account":master_account})

	result=cursor.fetchone()
	
	account_mgr=result[0]

	if check_manager(supervisor_id,account_mgr,connection,cursor) is True:
		return True

	else:
		return False

#given a master account, get the account_manager name
def get_manager_name(master_account,connection,cursor):

	cursor.execute("select account_mgr from accounts where account_no=:master_account",{"master_account":master_account})
	result=cursor.fetchone()
	account_mgr=result[0]

	cursor.execute("select name from personnel where pid=:account_mgr",{"account_mgr":account_mgr})
	name=cursor.fetchone()
	manager_name=name[0]

	return manager_name

#given a supervisor_id, get the account managers
def get_managers(pid,connection,cursor):

	cursor.execute("select pid from personnel where supervisor_pid=:pid",{"pid":pid})
	result=cursor.fetchall()

	manager_list=[]

	for i in result:
		manager_list.append(i[0])

	return manager_list

#sor the summary report by the differet of the sum of the internal cost and sum of theprice
def sort_report(managers,connection,cursor):

	manager_dict={}
	temp=[]
	for account_mgr in managers:
		cursor.execute("select sum(internal_cost) from service_agreements where master_account in (select account_no from accounts where account_mgr=:account_mgr)",{"account_mgr":account_mgr})
		result=cursor.fetchone()
		cost_sum=result[0]
		cursor.execute("select sum(price) from service_agreements where master_account in (select account_no from accounts where account_mgr=:account_mgr)",{"account_mgr":account_mgr})
		result=cursor.fetchone()
		price_sum=result[0]
		difference=abs(price_sum-cost_sum)
		manager_dict[account_mgr]=difference

	for i in sorted(manager_dict,key=manager_dict.get):
		temp.append(i)

	return temp
	
#list all the customers that can be chosed
def list_customers(pid,connection,cursor):

	cursor.execute("select account_no from accounts where account_mgr in (select pid from personnel where supervisor_pid=:pid)",{"pid":pid})
	result=cursor.fetchall()

	customers=[]

	for i in result:
		customers.append(i[0])

	return customers

#to create a new master account
def create_account_two(pid,connection,cursor):

	pid=str(pid)
	account_no=input("Please enter the account_no: ")

	while(check_account_no(account_no,connection,cursor) is False or check_new_account(account_no,connection,cursor) is False):

		if check_account_no(account_no,connection,cursor) is False:
			print("The account no entered are invalid, please enter again")
		else:
			print("The account number you entered is existed, please enter another account number")

		account_no=input("Please enter the account_no: ")

	customer_name=str(input("Plese enter the customer name: "))
	contact_info=str(input("Please enter the contact information: "))
	customer_type=str(input("Please enter the customer type: "))

	while(check_customer_type(customer_type,connection,cursor) is False):
		print("The customer type entered is not valid, please entered again")
		customer_type=str(input("Please enter the customer type: "))

	start_date=str(input("Please enter the start date(YYYY-MM-DD): "))
	end_date=str(input("Please enter the end date(YYYY-MM-DD): "))
	total_amount=0
	#total_amount=str(input("Please enter the total amount: "))

	insert_account="INSERT INTO accounts VALUES(:account_no,:account_mgr,:customer_name,:contact_info,:customer_type,:start_date,:end_date,:total_amount)"
	cursor.execute(insert_account,{"account_no":account_no,"account_mgr":pid,"customer_name":customer_name,"contact_info":contact_info,"customer_type":customer_type.lower(),"start_date":start_date,"end_date":end_date,"total_amount":total_amount})
	print('-------------------------------------------------------------------------------------------------------------------------')
	connection.commit()
	supervisor(pid,connection,cursor)

#to assign a new account to an account manager
def assign_account(pid,connection,cursor):

	manager=str(input("Please enter the account manager id: "))
	while(check_manager(pid,manager,connection,cursor) is False):
		print("This account does not managed by you, please enter another account manager id")
		manager=str(input("Please enter the account manager id: "))

	create_account_two(manager,connection,cursor)

#to create a summary report for a single customer
def summary_report_two(pid,master_account,name,connection,cursor):


	while(check_new_account(master_account,connection,cursor) is True):
		print("This master account does not exist, please enter again")
		master_account=str(input("PLease enter the master account: "))

	cursor.execute("select count(*) from service_agreements where master_account=:master_account",{"master_account":master_account})
	count=cursor.fetchone()
	count=count[0]

	cursor.execute("select sum(internal_cost) from service_agreements where master_account=:master_account",{"master_account":master_account})
	cost_sum=cursor.fetchone()
	cost_sum=cost_sum[0]

	cursor.execute("select sum(price) from service_agreements where master_account=:master_account",{"master_account":master_account})
	price_sum=cursor.fetchone()
	price_sum=price_sum[0]

	cursor.execute("select count(distinct waste_type) from service_agreements where master_account=:master_account",{"master_account":master_account})
	type_count=cursor.fetchone()
	type_count=type_count[0]

	print('-------------------------------------------------------------------------------------------------------------------------')
	print("The account manager of this account is "+str(name))
	print("The total number of service agreements is "+str(count))
	print("The sum of the prices is "+str(price_sum))
	print("The sum of the internal cost is "+str(cost_sum))
	print("The number of different waste types is "+str(type_count))
	print('-------------------------------------------------------------------------------------------------------------------------')

	connection.commit()
	supervisor(pid,connection,cursor)

#to select a customer that managed by the account manager who supervised by a supervisor
def customer_report(pid,connection,cursor):

	print("Plese select a customer from below list")
	customers=list_customers(pid,connection,cursor)
	print('-------------------------------------------------------------------------------------------------------------------------')
	print(*customers,sep='\n')
	print('-------------------------------------------------------------------------------------------------------------------------')
	master_account=str(input("Please enter the master account number: "))

	while(check_new_account(master_account,connection,cursor) is True or check_customer(pid,master_account,connection,cursor) is False):
		if check_new_account(master_account,connection,cursor) is True:
			print("This master account does not exist, please enter again")

		else:
			print("The master account entered is not matched, please enter another master account")

		master_account=str(input("PLease enter the master account: "))

	manager_name=get_manager_name(master_account,connection,cursor)
	summary_report_two(pid,master_account,manager_name,connection,cursor)

#given a account manager, return the master count and service agreements count
def get_count(account_mgr,connection,cursor):

	cursor.execute("select count(*) from service_agreements where master_account in (select account_no from accounts where account_mgr=:account_mgr)",{"account_mgr":account_mgr})
	result=cursor.fetchone()
	agreements_count=result[0]

	cursor.execute("select count(*) from accounts where account_mgr=:account_mgr",{"account_mgr":account_mgr})
	result_two=cursor.fetchone()
	master_count=result_two[0]

	return master_count,agreements_count

#to generate a summary report for account managers that supervisor supervise
def manager_report(pid,connection,cursor):

	managers=get_managers(pid,connection,cursor)

	sort_managers=sort_report(managers,connection,cursor)
	for account_mgr in sort_managers:

		master_count,agreements_count=get_count(account_mgr,connection,cursor)
		print('-------------------------------------------------------------------------------------------------------------------------')
		print("The total number of master agreements for account manager "+str(account_mgr)+" is "+str(master_count))
		print("The total number of service agreements for account manager "+str(account_mgr) +" is "+str(agreements_count))
		cursor.execute("select sum(internal_cost) from service_agreements where master_account in (select account_no from accounts where account_mgr=:account_mgr)",{"account_mgr":account_mgr})
		result=cursor.fetchone()
		cost_sum=result[0]
		print("The total sum of internal cost for account manager "+str(account_mgr) +" is "+str(round(cost_sum,2)))
		cursor.execute("select sum(price) from service_agreements where master_account in (select account_no from accounts where account_mgr=:account_mgr)",{"account_mgr":account_mgr})
		result=cursor.fetchone()
		price_sum=result[0]
		print("The total sum of price for account manager "+str(account_mgr) +" is "+str(round(price_sum,2)))
		print('-------------------------------------------------------------------------------------------------------------------------')


	connection.commit()
	supervisor(pid,connection,cursor)



