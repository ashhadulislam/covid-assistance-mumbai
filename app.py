from flask import Flask, render_template, request,send_from_directory, jsonify, url_for
from flask import redirect
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

import sys
sys.path.insert(0,'util/')
# from filename import function

import datetime
import pytz
from send_otp import send_otp_sms,send_otp_general_sms
from validate_phone import validate_phone

from read_sheet import get_sheet
from mumbai_helper import insert_into_gsheet_mumbai

from datetime import date


application = Flask(__name__)

# column number where status is mentioned in the sheet
request_status_index=5


# column number where benificiary number is mentioned in the sheet
beneficiary_contact_index=7
beneficiary_name_index=14




def convert_list_to_dict(the_request):
    dict_request={}
    dict_request["request_id"]=the_request[0]

    dict_request["name"]=the_request[1]
    dict_request["contact_num"]=the_request[2]
    # dict_request["lat"]=int(float(the_request[3]))
    # dict_request["lon"]=int(float(the_request[4]))
    dict_request["requestor_address"]=the_request[3]
    dict_request["request_status"]=the_request[4]

    dict_request["family_size"]=the_request[5]
    
    # a gap for beneficiary
    dict_request["volunteer_name"]=the_request[7]
    dict_request["vol_contact_num"]=the_request[8]

    dict_request["requestor_state"]=the_request[9]
    dict_request["requestor_district"]=the_request[10]
    dict_request["date_of_entry"]=the_request[11]
    dict_request["beneficiary_name"]=the_request[13]


    print(dict_request)
    return dict_request



def get_requests(sheetname,need_status):
    '''
    insert into the google sheet in the order
    name, contact_num,lat, lon, address,
    rice_qty, wheat_qty, oil_qty, daal_qty,
    request_status
    '''

    # if need_status=="Completed":
    #     sheetname="Daily_Completed"
    # elif need_status=="Pending":
    #     sheetname="Details_People"

    status,sheet=get_sheet(sheetname)
    if status == False:
        return sheet
    list_of_requests=(sheet.get_all_values())
    print("number of rows ",len(sheet.get_all_values()))
    print("number of columns ",len(sheet.get_all_values()[0]))
    

    list_requests=[]
    
    # skip the first request since it is heading
    for the_request in list_of_requests[1:]:
        print("status is ",the_request[request_status_index-1],need_status)
        

        if the_request[request_status_index-1]==need_status:

            # dict_request={}
            # dict_request["request_id"]=the_request[0]

            # dict_request["name"]=the_request[1]
            # dict_request["contact_num"]=the_request[2]
            # # dict_request["lat"]=int(float(the_request[3]))
            # # dict_request["lon"]=int(float(the_request[4]))
            # dict_request["requestor_address"]=the_request[3]
            # dict_request["request_status"]=the_request[4]

            # dict_request["rice_qty"]=the_request[5]
            # dict_request["wheat_qty"]=the_request[6]
            # dict_request["oil_qty"]=the_request[7]
            # dict_request["daal_qty"]=the_request[8]
            # # a gap for beneficiary
            # dict_request["volunteer_name"]=the_request[10]
            # dict_request["vol_contact_num"]=the_request[11]

            dict_request=convert_list_to_dict(the_request)


            list_requests.append(dict_request)

    return list_requests




###################### begin ####################################
###################### mumbai code###############################
#################################################################



@application.route('/mumbai')
def show_home_mumbai():    
    return render_template('base_mumbai.html')


@application.route('/addmumbaimeal')
def addmumbaimeal():    
    return render_template('addmumbaimeal.html')

@application.route('/contactmumbai')
def contactmumbai():    
    return render_template('contactmumbai.html')


@application.route('/pendingmumbai')
def pendingmumbai():    

    '''
    this function shows pending requests
    '''
    list_requests=get_requests(sheetname="Details_People_Mumbai",need_status="Pending")
    print("requests are ",list_requests)

    return render_template("pendingmumbai.html", items=list_requests)

    
@application.route('/completedmumbai',methods=["GET"])
def completedmumbai():
    '''
    this function shows completed requests
    '''    
    list_requests=get_requests(sheetname="Details_People_Mumbai",need_status="Completed")
    print("requests are ",list_requests)

    return render_template("completed.html", items=list_requests)    




@application.route('/load_in_sheet_mumbai',methods=["POST"])
def add_pending_request_mumbai():

    data_list=[]
    # print(request.form.keys)
    name=str(request.form['requestor_name'])
    contact_num=str(request.form['contact_num'])
    

    requestor_address=str(request.form['requestor_address'])
    requestor_state=str(request.form['requestor_state'])
    requestor_district=str(request.form['requestor_district'])

    request_status="Pending"

    # here get approx location from lat long
    
    volunteer_name=str(request.form['volunteer_name'])
    vol_contact_num=str(request.form['vol_contact_num'])
    
    

    num_in_family=str(request.form['fam_size'])
    # rice_qty=str(request.form['rice_qty'])
    # wheat_qty=str(request.form['wheat_qty'])
    # oil_qty=str(request.form['oil_qty'])
    # daal_qty=str(request.form['daal_qty'])

    print(requestor_state,requestor_district)    

    data_list.append(name)
    data_list.append(contact_num)

    # data_list.append(lat)
    # data_list.append(lon)
    data_list.append(requestor_address)   
    data_list.append(request_status) 

    data_list.append(num_in_family) 

    # data_list.append(rice_qty)
    # data_list.append(wheat_qty)
    # data_list.append(oil_qty)
    # data_list.append(daal_qty)

    data_list.append("")
    # above is for benificiary contact_num

    data_list.append(volunteer_name)
    data_list.append(vol_contact_num)

    data_list.append(requestor_state)
    data_list.append(requestor_district)
    today = date.today()    
    data_list.append(str(today.strftime("%d/%m/%Y")))


    print(name,contact_num,num_in_family)



    
    status = insert_into_gsheet_mumbai(data_list)

    # if status:
    #     message="Thanks for registering a needy family.\
    #     We will do our best to serve the request \
    #     as soon as possible. Requests are visible at \
    #     https://covid-help-2020.herokuapp.com/pendingmumbai"

    #     send_otp_general_sms(vol_contact_num,message)



    return render_template('intermediate-register-confirmation-mumbai.html')




@application.route('/checkoutmumbai',methods=["POST"])
def checkoutmumbai():

    list_ids_to_mark_complete=[]
    print(request.form.keys)
    for key,val in request.form.items():
        print(key)
        if key!="contact_num" and key!="contrib_name":
            list_ids_to_mark_complete.append(int(float(val)))
    print("to be completed",list_ids_to_mark_complete)

    benificiary_contact=request.form['contact_num']
    contrib_name=request.form['contrib_name']

    # some form validation here

    mobile_issue=False
    if benificiary_contact=="":
        mobile_issue=True
    
    if not benificiary_contact.isdecimal():
        mobile_issue=True

    if len(benificiary_contact)!=10:
        mobile_issue=True

    if mobile_issue:
        return "Please retry with proper mobile number"




    

    if len(list_ids_to_mark_complete)==0:
        return "Please go back and click on the check boxes \
        to select the requirements you want to fulfill."


    status,sheet=get_sheet("Details_People_Mumbai")
    if status==False:
        return sheet
    list_of_requests=(sheet.get_all_values())

    list_to_be_fulfilled=[]

    row_count=2
    for the_request in list_of_requests[1:]:
        if int(float(the_request[0])) in list_ids_to_mark_complete:
            # first create a dict out of the row

            dict_request=convert_list_to_dict(the_request)




            

            list_to_be_fulfilled.append(dict_request)
            # sheet.update_cell(row_count, request_status_index+1, "Completed")
            # sheet.update_cell(row_count, beneficiary_contact_index+1, str(benificiary_contact))
        row_count+=1

    print(list_to_be_fulfilled)

    dict_order={"contributor_number":str(benificiary_contact)}
    dict_order["order"]=list_to_be_fulfilled
    dict_order["contrib_name"]=contrib_name
    

    # now generate the otp    
    return_str=send_otp_sms(str(benificiary_contact).strip())
    dict_order["return_message"]=return_str

    
    return render_template("otp_payment_mumbai.html", items=dict_order)    



@application.route('/complete_payment_mumbai',methods=["POST"])
def complete_payment_mumbai():
    list_ids_to_mark_complete=[]
    print(request.form.keys)
    for key,val in request.form.items():
        print("k is ",key)
        if key!="contact_num" and key!="otp_num" and key!="return_message" and key!="contrib_name":
            list_ids_to_mark_complete.append(int(float(val)))
    print(list_ids_to_mark_complete)
    benificiary_contact=request.form['contact_num']
    otp_num=request.form['otp_num']
    # amount_pledged=request.form['amount_pledged']
    contrib_name=request.form['contrib_name']

    

    

    # now to check if otp matches with the otp mentioned in the sheet
    # also check for expired otp

    is_valid=True
    is_valid=validate_phone(benificiary_contact,otp_num)

    print("checked the otp")

    if is_valid:
        

        




        status,sheet=get_sheet("Details_People_Mumbai")
        if status==False:
            return sheet
        list_of_requests=(sheet.get_all_values())

        list_to_be_fulfilled=[]

        row_count=2


        # we'll check if the request ids match
        for the_request in list_of_requests[1:]:
            if int(float(the_request[0])) in list_ids_to_mark_complete:            
                sheet.update_cell(row_count, request_status_index, "Completed")
                sheet.update_cell(row_count, beneficiary_contact_index,
                 str(benificiary_contact))
                sheet.update_cell(row_count, beneficiary_name_index,
                 str(contrib_name))

                
            row_count+=1



        return render_template("thank-you-mumbai.html")
    else:
        return "Some issue with your OTP, please go back and check out again"





######################### end ###################################
###################### mumbai code###############################
#################################################################

@application.route('/')
def show_home():    
    return render_template('base.html')



@application.route('/addneedy')
def addneedy():    
    return render_template('addneedy.html')

@application.route('/contact')
def contact():    
    return render_template('contact.html')




@application.route('/pending',methods=["GET"])
def pending():
    '''
    this function shows pending requests
    '''
    list_requests=get_requests(sheetname="Details_People",need_status="Pending")
    print("requests are ",list_requests)

    return render_template("pending.html", items=list_requests)


@application.route('/completed',methods=["GET"])
def complete():
    '''
    this function shows completed requests
    '''    
    list_requests=get_requests(sheetname="Daily_Completed",need_status="Completed")
    print("requests are ",list_requests)

    return render_template("completed.html", items=list_requests)    




@application.route('/checkout',methods=["POST"])
def checkout():

    # list_ids_to_mark_complete=[]
    # print(request.form.keys)
    # for key,val in request.form.items():
    #     print(key)
    #     if key!="contact_num":
    #         list_ids_to_mark_complete.append(int(float(val)))
    # print(list_ids_to_mark_complete)

    benificiary_contact=request.form['contact_num']
    amount_pledged=request.form['amount_pledged']
    contrib_name=request.form['contrib_name']

    # some form validation here

    mobile_issue=False
    if benificiary_contact=="":
        mobile_issue=True
    
    if not benificiary_contact.isdecimal():
        mobile_issue=True

    if len(benificiary_contact)!=10:
        mobile_issue=True

    if mobile_issue:
        return "Please retry with proper mobile number"




    

    # if len(list_ids_to_mark_complete)==0:
    #     return "Please go back and click on the check boxes \
    #     to select the requirements you want to fulfill."


    # status,sheet=get_sheet("Details_People")
    # if status==False:
    #     return sheet
    # list_of_requests=(sheet.get_all_values())

    # list_to_be_fulfilled=[]

    # row_count=2
    # for the_request in list_of_requests[1:]:
    #     if int(float(the_request[0])) in list_ids_to_mark_complete:
    #         # first create a dict out of the row

    #         dict_request=convert_list_to_dict(the_request)




            

    #         list_to_be_fulfilled.append(dict_request)
    #         # sheet.update_cell(row_count, request_status_index+1, "Completed")
    #         # sheet.update_cell(row_count, beneficiary_contact_index+1, str(benificiary_contact))
    #     row_count+=1

    # print(list_to_be_fulfilled)
    dict_order={"contributor_number":str(benificiary_contact),"amount_pledged":amount_pledged}
    dict_order["contrib_name"]=contrib_name
    

    # now generate the otp    
    return_str=send_otp_sms(str(benificiary_contact).strip())
    dict_order["return_message"]=return_str

    
    return render_template("otp_payment.html", items=dict_order)    






@application.route('/complete_payment',methods=["POST"])
def complete_payment():
    # list_ids_to_mark_complete=[]
    # print(request.form.keys)
    # for key,val in request.form.items():
    #     print(key)
    #     if key!="contact_num" and key!="otp_num" and key!="return_message":
    #         list_ids_to_mark_complete.append(int(float(val)))
    # print(list_ids_to_mark_complete)
    benificiary_contact=request.form['contact_num']
    otp_num=request.form['otp_num']
    amount_pledged=request.form['amount_pledged']
    contrib_name=request.form['contrib_name']

    

    

    # now to check if otp matches with the otp mentioned in the sheet
    # also check for expired otp

    is_valid=True
    is_valid=validate_phone(benificiary_contact,otp_num)

    print("checked the otp")

    if is_valid:
        # add amount to sheet

        status,sheet=get_sheet("Payment Local")
        if status==False:
            return sheet
        data_list=[contrib_name,benificiary_contact,amount_pledged]

        
        my_date = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))        
        data_list.append(str(my_date))
        index=len(sheet.get_all_values())+1
        sheet.insert_row(data_list, index)





        # status,sheet=get_sheet("Details_People")
        # if status==False:
        #     return sheet
        # list_of_requests=(sheet.get_all_values())

        # list_to_be_fulfilled=[]

        # row_count=2


        # we'll check if the request ids match
        # for the_request in list_of_requests[1:]:
        #     if int(float(the_request[0])) in list_ids_to_mark_complete:            
        #         sheet.update_cell(row_count, request_status_index+1, "Completed")
        #         sheet.update_cell(row_count, beneficiary_contact_index+1,
        #          str(benificiary_contact))
        #     row_count+=1



        return redirect("https://imjo.in/U6X3pf")
    else:
        return "Some issue with your OTP, please go back and check out again"









def insert_into_gsheet(data_list):
    '''
    insert into the google sheet in the order
    name, contact_num,lat, lon, address,
    rice_qty, wheat_qty, oil_qty, daal_qty,
    request_status
    '''
    status,sheet=get_sheet("Details_People_Intermediate")
    if status==False:
        return sheet
    
    row = data_list
    index = len(sheet.get_all_values())+1
    print("last id ",sheet.get_all_values()[-1][0])
    if len(sheet.get_all_values())>=2:
        request_id=int(sheet.get_all_values()[-1][0])+1
    else:
        # first request
        request_id=1
    row=[request_id]+row
    sheet.insert_row(row, index)
    return True



@application.route('/load_in_sheet',methods=["POST"])
def add_pending_request():

    data_list=[]
    # print(request.form.keys)
    name=str(request.form['requestor_name'])
    contact_num=str(request.form['contact_num'])

    # lat=str(request.form['mosque_lat'])
    # if lat=="":
    #     lat=0

    # lon=str(request.form['mosque_lon'])
    # if lon=="":
    #     lon=0

    requestor_address=str(request.form['requestor_address'])
    requestor_state=str(request.form['requestor_state'])
    requestor_district=str(request.form['requestor_district'])

    request_status="Unverified"

    # here get approx location from lat long
    
    volunteer_name=str(request.form['volunteer_name'])
    vol_contact_num=str(request.form['vol_contact_num'])
    
    

    num_in_family=str(request.form['fam_size'])
    # rice_qty=str(request.form['rice_qty'])
    # wheat_qty=str(request.form['wheat_qty'])
    # oil_qty=str(request.form['oil_qty'])
    # daal_qty=str(request.form['daal_qty'])

    print(requestor_state,requestor_district)

    

    data_list.append(name)
    data_list.append(contact_num)

    # data_list.append(lat)
    # data_list.append(lon)
    data_list.append(requestor_address)   
    data_list.append(request_status) 

    data_list.append(num_in_family) 

    # data_list.append(rice_qty)
    # data_list.append(wheat_qty)
    # data_list.append(oil_qty)
    # data_list.append(daal_qty)

    data_list.append("")
    # above is for benificiary contact_num

    data_list.append(volunteer_name)
    data_list.append(vol_contact_num)

    data_list.append(requestor_state)
    data_list.append(requestor_district)

    today = date.today()
    
    data_list.append(str(today.strftime("%d/%m/%Y")))


    




    print(name,contact_num,num_in_family)



    
    status = insert_into_gsheet(data_list)

    if status:
        message="Thanks for registering a needy family.\
        Once the background check is complete, \
        the family you enlisted will appear at \
        https://covid-help-2020.herokuapp.com/pending"

        send_otp_general_sms(vol_contact_num,message)



    return render_template('intermediate-register-confirmation.html')



if __name__ == "__main__":
    
    
    application.run(debug=True)




