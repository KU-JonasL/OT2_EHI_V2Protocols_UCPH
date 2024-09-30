import pandas as pd 
from io import StringIO
import tempfile
from math import *

#read_file = pd.read_excel("template\Template_CSV_LibraryInput.xlsx")
#df = pd.DataFrame(read_file)


#df['DNA volume (ul) for Covaris'] = df['DNA volume (ul) for Covaris'].fillna(0)
#df['Water volume (ul) for Covaris'] = df['Water volume (ul) for Covaris'].fillna(0)
#df['Adaptor concentration (nM)'] = df['Adaptor concentration (nM)'].fillna(0)

#print(df)

#print(df['Water volume (ul) for Covaris'])

#for i in range(0,96):
#    print(df['Well Position'][i])

#userinput = "user_data/User_Input.csv"
#df = pd.DataFrame(pd.read_csv(f'{userinput}', header=0)) 
#print(df)
#Info = df['User'][0]
#print(Info)



#csv_userinput = '''User, Protocol, Input, email
#Jonas, Library, LVL, jonas.lauritsen@sund.ku.dk'''

#data=StringIO(csv_userinput)

#df = pd.read_csv(data,header=0)
#print(df)
#print("Hellow")
#print(df['User'][0])



#userdata = "Other\Template_CSV_LibraryInput.csv"


## Set uploaded file and secure name
#uploaded_file = userdata
                   
## Create a temporary file
#with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
    #temp_file_path = temp_file.name
    #uploaded_file.save(temp_file_path)

    ## Load and cleanup for the userdata
    #temp_userdata_csv = pd.read_csv(userdata)
    #userdata = [tuple(temp_userdata_csv.columns)] + [tuple(row) for row in temp_userdata_csv.values]

    #csv_data_values = "\n".join([f"({', '.join(map(str, row))})" for row in temp_userdata_csv.values])
    #csv_data_raw_str = f"{', '.join(temp_userdata_csv.columns)}\n{csv_data_values}"
    #userdata = csv_data_raw_str.replace("nan", "").replace("(", "").replace(")", "").replace(",",".").replace(";",",")

#print(userdata)
#print(type(userdata))


# text = "Hej med dig"
# a = text.find("dig")
# print(a)
# print(bool(a))



csv_userinput = '''
Protocol, User, SampleNumber, InputFormat, OutputFormat, Naming
Extraction, Jonas4, 95, DeepwellPlate, PCRstrip, Jonas4_Extraction_20240124
'''



csv_input_temp = StringIO(csv_userinput)
user_input = pd.read_csv(csv_input_temp)
# csv_data_temp = StringIO(csv_userdata)
# user_data = pd.read_csv(csv_data_temp)

# print(user_input)
print(user_input)

Col_number = user_input['Protocol']
print(Col_number)
Col_number = user_input[' Naming']
print(Col_number)

Sample_Number=int(user_input[' Sample Number'][0])
Col_Number = int(ceil(Sample_Number/8))
print(Col_Number)

# user_data.dropna(subset=['Sample ID'], inplace=True)
# print(user_data)

# csv_data_values = "\n".join([f"{', '.join(map(str, row))}" for row in user_data.values])
# csv_data_raw_str = f"{', '.join(user_data.columns)}\n{csv_data_values}"
# userdata = csv_data_raw_str.replace("nan", "")
# print(userdata)