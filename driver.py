import sqlite3

global connection, cursor

def driver(pid,connection,cursor):
	

	print("What function do you want to use? ")
	print("1: List tours informaion")
	print("2: Log out")

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
			break

		else:
			print("Invalid command,please select again")
			continue

	connection.commit()

#given a driver id, return the location
def get_information(service_no,connection,cursor):

	cursor.execute("select location,waste_type,local_contact from service_agreements where service_no=:service_no",{"service_no":service_no})
	result=cursor.fetchall()

	return result[0]

#given a date range, return all the service_no in this range
def get_service_no(start_date,end_date,driver_id,connection,cursor):

	comma="'"
	command="select service_no from service_fulfillments where driver_id=:driver_id and date_time between "+comma+str(start_date)+comma+" and "+comma+str(end_date)+comma 
	cursor.execute(command,{"driver_id":driver_id})

	result=cursor.fetchall()

	service_no=[]

	for i in result:
		service_no.append(i[0])

	return service_no

#given a service_no, return the cid_pick_up and cid_drop_off
def get_container_id(service_no,driver_id,connection,cursor):

	cursor.execute("select cid_pick_up,cid_drop_off from service_fulfillments where service_no=:service_no and driver_id=:driver_id",{"service_no":service_no,"driver_id":driver_id})
	result=cursor.fetchone()

	return result

#list the tour informations about a driver
def list_information(pid,connection,cursor):


	start_date=str(input("Please enter the start date(YYYY-MM-DD): "))
	end_date=str(input("Please enter the end date(YYYY-MM-DD): "))
	service_no=get_service_no(start_date,end_date,pid,connection,cursor)
	print('--------------------------------------------------------------------------------------------------------------------------------------')
	print("location".ljust(30)+"waste type".ljust(33)+"local contact".ljust(34)+"cid_pick_up".ljust(24)+"cid_drop_off")
	print('--------------------------------------------------------------------------------------------------------------------------------------')
	for i in service_no:
		containers=get_container_id(i,pid,connection,cursor)
		informations=get_information(i,connection,cursor)
		
		print(str(informations[0]).ljust(30)+str(informations[1]).ljust(33)+str(informations[2]).ljust(34)+str(containers[0]).ljust(24)+str(containers[1]))

	print('--------------------------------------------------------------------------------------------------------------------------------------')

	driver(pid,connection,cursor)

	connection.commit()

	