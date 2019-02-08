import sqlite3
import re
global connection, cursor

def account_manager(pid,connection,cursor):

	print("What function do you want to use? ")
	print("1: List information of a customer")
	print("2: Create a new master account")
	print("3: Add a new service agreeement")
	print("4: Create a summary report")
	print("5: Log out")

	while(1):
		try:
			choice=int(input("Enter your choice: "))
		except:
			print("Invalid command,please select again")
			continue
		if choice == 1:
			list_information(pid,connection,cursor)
			break			

		elif choice == 2:
			create_account(pid,connection,cursor)
			break

		elif choice == 3:
			create_service_agreement(pid,connection,cursor)
			break

		elif choice == 4:
			summary_report(pid,connection,cursor)
			break

		elif choice == 5:
			break

		else:
			print("Invalid command,please select again")
			continue

	connection.commit()

#to check if the account is managered by this account manager
def check_account(account,pid,connection,cursor):

	cursor.execute("SELECT account_no from accounts where account_mgr=:pid",{"pid":pid})

	result=cursor.fetchall()
	accounts=[]
	status=False

	for i in result:
		accounts.append(i[0])

	for i in accounts:
		result=re.match(i,account,re.IGNORECASE)
		if result != None:
			status = True

	return status

#to check if the account no is already existed
def check_new_account(account,connection,cursor):

	cursor.execute("SELECT account_no from accounts")

	result=cursor.fetchall()
	status=True
	accounts=[]

	for i in result:
		accounts.append(i[0])

	for i in accounts:
		result=re.match(i,account,re.IGNORECASE)
		if result != None:
			status = False

	return status

#to check the waste types
def check_waste(waste_type,connection,cursor):

	cursor.execute("SELECT waste_type from waste_types")
	result=cursor.fetchall()
	status=False
	types=[]

	for i in result:
		types.append(i[0])

	for i in types:
		result=re.match(i,waste_type,re.IGNORECASE)
		if result != None:
			status = True

	return status

#given a customer type, check if it is valid
def check_customer_type(types,connection,cursor):

	status=False
	customer_types=['municipal','commercial','industrial','residential']

	for i in customer_types:
		result=re.match(i,types,re.IGNORECASE)
		if result != None:
			status = True

	return status

#given an account no, check if it include characters
def check_account_no(account,connection,cursor):

	try:
		int(account)
		return True
	except:
		return False

#to caculate next available service_no
def calculate_service_no(connection,cursor):

	cursor.execute("SELECT service_no from service_agreements")
	result=cursor.fetchall()
	number_list=[]

	for i in result:
		number_list.append(int(i[0]))

	number=max(number_list)

	return number+1

#given a price and a master account, update the price to the total amount in the account
def update_amount(master_account,price,connection,cursor):
	
	cursor.execute("SELECT total_amount from accounts where account_no=:master_account",{"master_account":master_account})
	result=cursor.fetchone()

	amount=result[0]
	amount=float(amount)
	price=float(price)

	amount=amount+price

	cursor.execute("UPDATE accounts set total_amount=:amount where account_no=:master_account",{"amount":amount,"master_account":master_account})

#to list all the information about an account
def list_information(pid,connection,cursor):

	while(1):
		account=input("Please enter the master account you want to list ")
		
		if check_account(account,pid,connection,cursor) is True:

			cursor.execute("select * from accounts where account_no=:account",{"account":account})
			result=cursor.fetchone()
			print('-----------------------------------------------------------------------------------------------------------------------------------------------------------')
			print("account_no".ljust(13)+"account_mgr".ljust(18)+"customer_name".ljust(23)+"contact_info".ljust(21)+"customer_type".ljust(31)+"start_date".ljust(17),"end_date".ljust(17)+"total_amount")
			print('-----------------------------------------------------------------------------------------------------------------------------------------------------------')
			print(result[0].ljust(13)+result[1].ljust(18)+result[2].ljust(23)+result[3].ljust(21)+result[4].ljust(31)+result[5].ljust(17)+result[6].ljust(17),result[7])
			print('-----------------------------------------------------------------------------------------------------------------------------------------------------------')
			print('-----------------------------------------------------------------------------------------------------------------------------------------------------------')
			cursor.execute("select * from service_agreements where master_account=:account order by service_no",{"account":account})
			service_agreements=cursor.fetchall()
			print("service_no".ljust(13)+"master_account".ljust(18)+"location".ljust(23)+"waste_type".ljust(21)+"pick_up_schedule".ljust(31)+"local_contact".ljust(17),"internal_cost".ljust(17),"price")
			print('-----------------------------------------------------------------------------------------------------------------------------------------------------------')
			for i in service_agreements:
				print(i[0].ljust(13)+i[1].ljust(18)+i[2].ljust(23)+i[3].ljust(21)+i[4].ljust(31)+i[5].ljust(17),str(i[6]).ljust(17),i[7])


			print('-----------------------------------------------------------------------------------------------------------------------------------------------------------')
			account_manager(pid,connection,cursor)

			break

		else:
			print("The master account you inputed does not exist or you have no access right on that account")
			continue

	connection.commit()

#to create a new master account
def create_account(pid,connection,cursor):

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
	account_manager(pid,connection,cursor)

#to add new service agreement
def create_service_agreement(pid,connection,cursor):

	service_no=str(calculate_service_no(connection,cursor))
	master_account=str(input("PLease enter the master account: "))
	
	while(check_new_account(master_account,connection,cursor) is True):
		print("This master account does not exist, please enter again")
		master_account=str(input("PLease enter the master account: "))

	while(check_account(master_account,pid,connection,cursor) is False):
		if check_new_account(master_account,connection,cursor) is False:
			print("This account does not managed by you, please select another account")
		else:
			print("This master account does not exist, please enter again")
		master_account=str(input("PLease enter the master account: "))

	location=str(input("Please enter the location: "))
	waste_type=str(input("Please enter the waste type: "))

	while(check_waste(waste_type,connection,cursor) is False):

		print("The waste type is not valid, please enter again")
		waste_type=str(input("Please enter the waste type: "))

	pick_up_schedule=str(input("Please enter the pick up schedule: "))
	local_contact=str(input("Please enter the local contact: "))
	internal_cost=input("Please enter the internal cost: ")
	price=input("Please enter the price: ")

	insert_agreement="INSERT INTO service_agreements VALUES(:service_no,:master_account,:location,:waste_type,:pick_up_schedule,:local_contact,:internal_cost,:price)"
	cursor.execute(insert_agreement,{"service_no":service_no,"master_account":master_account,"location":location,"waste_type":waste_type,"pick_up_schedule":pick_up_schedule,"local_contact":local_contact,"internal_cost":internal_cost,"price":price})
	print('-------------------------------------------------------------------------------------------------------------------------')

	update_amount(master_account,price,connection,cursor)
	connection.commit()
	account_manager(pid,connection,cursor)

#to create a summary report for a single customer
def summary_report(pid,connection,cursor):

	master_account=str(input("Please enter the master account: "))

	while(check_new_account(master_account,connection,cursor) is True or check_account(master_account,pid,connection,cursor) is False):
		if check_new_account(master_account,connection,cursor) is True :
			print("This master account does not exist, please enter again")
		else:
			print("This account does not managed by you, please select another account")
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
	print("The total number of service agreements is "+str(count))
	print("The sum of the prices is "+str(price_sum))
	print("The sum of the internal cost is "+str(cost_sum))
	print("The number of different waste types is "+str(type_count))
	print('-------------------------------------------------------------------------------------------------------------------------')

	connection.commit()
	account_manager(pid,connection,cursor)





