from read_sheet import get_sheet

def insert_into_gsheet_mumbai(data_list):
    '''
    insert into the google sheet in the order
    name, contact_num,lat, lon, address,
    rice_qty, wheat_qty, oil_qty, daal_qty,
    request_status
    '''
    status,sheet=get_sheet("Details_People_Mumbai")
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
