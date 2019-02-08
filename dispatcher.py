import sqlite3
import re
global connection, cursor

def dispatcher(pid,connection,cursor):
	
	print("What function do you want to use? ")
	print("1: Create an entry")
	print("2: Log out")

	while(1):
		try:
			choice=int(input("Enter your choice: "))
		except:
			print("Invalid command,please select again")
			continue
		if choice == 1:
			create_entry(pid,connection,cursor)
			break			

		elif choice == 2:
			break

		else:
			print("Invalid command,please select again")
			continue

	connection.commit()

#given a service number, check if it is in service_agreements table
def check_service_no(agreement,connection,cursor):

	cursor.execute("select service_no from service_agreements")
	result=cursor.fetchall()

	agreement_list=[]

	for i in result:
		agreement_list.append(i[0])

	if agreement in agreement_list:
		return True

	else:

		return False

#given a driver number, check if it is in drivers table
def check_driver(driver,connection,cursor):

	cursor.execute("select pid from drivers")
	result=cursor.fetchall()

	drivers_list=[]

	for i in result:
		drivers_list.append(i[0])

	if driver in drivers_list:
		return True

	else:
		return False

#given a driver pid, check if he own a truck
def check_own_truck(driver,connection,cursor):

	cursor.execute("select owned_truck_id from drivers where pid=:driver",{"driver":driver})
	result=cursor.fetchone()
	status=result[0]

	if status == None:
		return False

	else:
		return status

#given an truck id, check if it is in trucks table:
def check_truck(truck,connection,cursor):
	cursor.execute("select truck_id from trucks where truck_id not in (select owned_truck_id from drivers where owned_truck_id is not NULL)")
	result=cursor.fetchall()

	for i in result:
		if i[0] == truck:
			return True
	else:

		return False

#given a service_no, get the master account
def get_master_account(service_no,connection,cursor):

	cursor.execute("select master_account from service_agreements where service_no=:service_no",{"service_no":service_no})
	result=cursor.fetchone()

	return result[0]

#given a master account, return the container that he should pick up next time
def get_pick_up(master_account,connection,cursor):

	cursor.execute("select cid_drop_off from service_fulfillments where master_account=:master_account order by date_time desc limit 1",{"master_account":master_account})
	result=cursor.fetchone()

	if result != None:
		cid_pick_up=result[0]

		return cid_pick_up

	else:
		return '0000'

#given a master account, return all the available list
def get_waste_type(master_account,connection,cursor):

	cursor.execute("select waste_type from service_agreements where master_account=:master_account",{"master_account":master_account})
	result=cursor.fetchall()

	container_list=[]

	for i in result:

		container_list.append(i[0])

	return container_list

#given a list of waste type, return the containers that has the same type with it
def get_available_container(master_account,connection,cursor):

	waste_type=get_waste_type(master_account,connection,cursor)

	cursor.execute("SELECT c.container_id FROM containers c WHERE NOT EXISTS (SELECT * FROM service_fulfillments s WHERE s.cid_drop_off = c.container_id) UNION SELECT c.container_id FROM containers c WHERE (SELECT MAX(date_time) FROM service_fulfillments s WHERE s.cid_pick_up = c.container_id) > (SELECT MAX(date_time) FROM service_fulfillments s WHERE s.cid_drop_off = c.container_id)")
	result=cursor.fetchall()

	cid_list=[]
	temp=[]
	final=[]
	for i in result:
		cid_list.append(i[0])

	for i in waste_type:
		cursor.execute("select container_id from container_waste_types where waste_type=:waste_type",{"waste_type":i})
		cid=cursor.fetchall()
		for x in cid:
			temp.append(x[0])

	for i in temp:
		if i in cid_list:
			final.append(i)

	return list(set(final))

#create an entry in service_fulfillments table
def create_entry(pid,connection,cursor):

	agreement=str(input("Please enter the service_no: "))
	while(check_service_no(agreement,connection,cursor) is False):
		print("The service number entered does not exist,please enter again")
		agreement=str(input("Please enter the service_no: "))	

	driver_id=str(input("Please enter the driver id: "))
	while(check_driver(driver_id,connection,cursor) is False):
		print("The driver number entered does not exist,please enter again")
		driver_id=str(input("Please enter the driver id: "))

	if check_own_truck(driver_id,connection,cursor) is False:
	 	truck_id=str(input("Please enter a truck id: "))
	 	while(check_truck(truck_id,connection,cursor) is False):
	 		print("The truck id entered are not available, please enter again")
	 		truck_id=str(input("Please enter a truck id: "))
	else:
		truck_id=check_own_truck(driver_id,connection,cursor)

	master_account=get_master_account(agreement,connection,cursor)

	cid_pick_up=get_pick_up(master_account,connection,cursor)

	containers_list=get_available_container(master_account,connection,cursor)

	if len(containers_list) != 0:
		print("There is a list of available containers to drop off")
		print('-------------------------------------------------------------------------------------------------------------------------')
		print(*containers_list,sep='\n')
		print('-------------------------------------------------------------------------------------------------------------------------')

		cid_drop_off=str(input("Please select a container id to drop off: "))

		while(cid_drop_off not in containers_list):
			print("The cid entered are currently not available, please enter another one")
			cid_drop_off=str(input("Please enter a container id to drop off: "))

		date_time=str(input("Please enter a date time(YYYY-MM-DD): "))
		insert_fulfillments="INSERT INTO service_fulfillments VALUES(:date_time,:master_account,:service_no,:truck_id,:driver_id,:cid_drop_off,:cid_pick_up)"
		cursor.execute(insert_fulfillments,{"date_time":date_time,"master_account":master_account,"service_no":agreement,"truck_id":truck_id,"driver_id":driver_id,"cid_drop_off":cid_drop_off,"cid_pick_up":cid_pick_up})

		dispatcher(pid,connection,cursor)
		connection.commit()

	else:
		print("There are no available containers to drop off, please select another agreement")
		dispatcher(pid,connection,cursor)
		connection.commit()

	
	











