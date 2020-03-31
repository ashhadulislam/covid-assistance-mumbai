from twilio.rest import Client
from os import environ
from otp_gen import generate_otp 
from datetime import datetime

import time
import hashlib

from read_sheet import get_sheet

otp_index=3
time_index=1
number_index=2
# above in the sheet
# in code subtract 1

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
def send_otp_sms(user_phone):
	account_sid = environ.get('account_sid')
	auth_token =  environ.get('auth_token')
	

	

	#first store it into sheet
	
	# get data from sheet
	sheetname="OTP_Record"
	status,sheet=get_sheet(sheetname)

	otp_records=sheet.get_all_values()
	number_exists=False
	return_str="OK"

	row_count=2
	for otp_record in otp_records[1:]:
		# number match
		if user_phone==otp_record[number_index-1]:
			return_str="OTP has been already sent. Please wait 3 minutes before re generating"
			number_exists=True
			user_otp=otp_record[otp_index-1]
			print("Otp already here, lets check the time")
			otp_gen_time=int(otp_record[time_index-1])
			print("Otp was generated at ",otp_gen_time)
			# get the current time
			secnow = time.time()
			print("current time ",secnow)
			diff=(secnow-otp_gen_time)//60
			print("Difference in time is ",diff)
			if diff>=3:
				# more than 3 minutes, can generate new otp
				user_otp = generate_otp(user_phone)
				print("New otp is this ",user_otp)

				# update time stamp
				sheet.update_cell(row_count, time_index, secnow)
				# update with new otp
				sheet.update_cell(row_count, otp_index, user_otp)
				
				return_str="OTP has been sent/recorded"
		row_count+=1

	if not number_exists:
		user_otp = generate_otp(user_phone)
		print("New user, otp is ",user_otp)
		# make a new entry in the sheet
		index = len(sheet.get_all_values())+1
		row=[time.time(),user_phone,user_otp]

		sheet.insert_row(row, index)
		return_str="OTP has been sent/recorded"



	if return_str=="OTP has been sent/recorded":
		# send sms to user

		client = Client(account_sid, auth_token)

		if "+91" not in user_phone and len(user_phone)!=13:
			user_phone="+91"+user_phone

		print("sending to ",user_phone)

		message = client.messages.create(
		     body   =  'Your OTP for Covid Help is :'+str(user_otp),
		     from_  =  environ.get('reg_phone'),
		     to     =  str(user_phone),
		 )

		print(message.sid)

	# return to 
	return return_str








def send_otp_general_sms(user_phone,message):
	account_sid = environ.get('account_sid')
	auth_token =  environ.get('auth_token')

	client = Client(account_sid, auth_token)
	if "+91" not in user_phone and len(user_phone)!=13:
		user_phone="+91"+user_phone

	message = client.messages.create(
		     body   =  str(message),
		     from_  =  environ.get('reg_phone'),
		     to     =  str(user_phone),
		 )

	print(message.sid)
	print("message sent probably")




	
	

