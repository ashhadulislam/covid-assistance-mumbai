from read_sheet import get_sheet
import time

otp_index=3
time_index=1
number_index=2
# above in the sheet
# in code subtract 1


def validate_phone(user_phone,user_given_otp):
    # correct_otp = get_otp(user_phone)

    # check if the user number exists in the list

	sheetname="OTP_Record"
	status,sheet=get_sheet(sheetname)

	otp_records=(sheet.get_all_values())
	number_exists=False


	for otp_record in otp_records[1:]:    
		# number match
		if user_phone==otp_record[number_index-1]:
			user_otp=otp_record[otp_index-1]			
			otp_gen_time=int(otp_record[time_index-1])
			# get the current time
			secnow = time.time()
			diff=(secnow-otp_gen_time)//60
			print("Difference in time is ",diff)
			if diff>=3:
				return False
			else:
				if user_otp!=user_given_otp:
					return False
				else:
					return True
	return False




    # user_otp = str(user_otp)
    # if(user_otp == correct_otp):
    #      return True
    # return False


