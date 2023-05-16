# -*- coding: utf-8 -*-
"""
Created on Sat May 13 17:45:32 2023

@author: yoran
"""
import numpy as np
import tkinter as tk
import tkinter.messagebox
import customtkinter
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import requests
import io
from datetime import timedelta,datetime
from pandas import json_normalize
import time
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
from sklearn.decomposition import PCA




# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")
root = customtkinter.CTk()
root.title("Ma1 Project")
# set the dimensions of the root window to the size of the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry("{}x{}+0+0".format(screen_width, screen_height*0.9))

# open the root window in the top left corner of the screen
root.geometry("+0+0")
root.wm_iconbitmap('air-element.ico')
# configure grid layout (4x4)

root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure((2, 3), weight=0)
root.grid_rowconfigure((0, 1, 2), weight=1) 
#bruface_image =customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))

dataframes = {}
names = []
overlap={}

def main():


    # create sidebar frame with widgets
    sidebar_frame = customtkinter.CTkFrame(root, fg_color=('dark grey','light grey'),width=50, corner_radius=0)
    sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
    
    sidebar_frame2 = customtkinter.CTkFrame(root, fg_color=('dark grey','light grey'),width=50, corner_radius=0)
    sidebar_frame2.grid(row=3, column=0,sticky="nsew")

    
    # Create the button and option box
    sidebar_button_0 = customtkinter.CTkButton(sidebar_frame,text = 'Browse files', command=load_file)
    sidebar_button_0.grid(row=0, column=0, padx=20, pady=10)   
    
    option_box = customtkinter.CTkOptionMenu(sidebar_frame, values=["Qsenseair", "Airhor", "Atmotube"],command=import_data)
    option_box.grid(row=1, column=0, padx=20, pady=10)  
    option_box.set("Download data")
    sidebar_button_1 = customtkinter.CTkButton(sidebar_frame,text='Plot', command=frame_selectplot)
    sidebar_button_1.grid(row=2, column=0, padx=20, pady=10)
    sidebar_button_2 = customtkinter.CTkButton(sidebar_frame,text='Correlate', command=frame_correlate)
    sidebar_button_2.grid(row=3, column=0, padx=20, pady=10)
    sidebar_button_3 = customtkinter.CTkButton(sidebar_frame,text='Overlap', command=frame_selectplot2)
    sidebar_button_3.grid(row=4, column=0, padx=20, pady=10)
    
    appearance_mode_optionemenu = customtkinter.CTkOptionMenu(sidebar_frame2, values=["Light", "Dark", "System"],command=change_appearance_mode_event)
    appearance_mode_optionemenu.grid(row=1, column=0, padx=20, pady=(10, 10))
    appearance_mode_optionemenu.set("Appearance Mode:")  # set initial value

    scaling_optionemenu = customtkinter.CTkOptionMenu(sidebar_frame2, values=["80%", "90%", "100%", "110%", "120%"],command=change_scaling_event)
    scaling_optionemenu.grid(row=3, column=0, padx=20, pady=(10, 20))
    scaling_optionemenu.set("UI Scaling:")  # set initial value

    


"get data"
def import_data(sensor: str):
    if sensor=='Qsenseair':
        frame_qsens()
    elif sensor=='Atmotube':
        frame_atmo()
    elif sensor=='Airhor':
        frame_airhor()
        
def frame_qsens():
    global txt_process
    frame_qsenseair = customtkinter.CTkFrame(root,fg_color="transparent", width=50,corner_radius=0)
    frame_qsenseair.grid(row=0, column=1, rowspan=4, columnspan=4, sticky="nsew")
    frame_qsenseair.grid_columnconfigure((1, 2, 3), weight=1) 

    downl_qsenseair(frame_qsenseair)

    

def downl_qsenseair(frame_qsenseair):
    global redirect
    textbox = customtkinter.CTkTextbox(frame_qsenseair)
    textbox.grid(row=0, column=0,rowspan=2, columnspan=2,padx=20, pady=10, sticky="nsew")
    redirect = RedirectText(textbox)

    pd.options.mode.chained_assignment = None #Disable Pandas warnings about chained assignments.
    # Read the sensors' MAC addresses and dates csv file
    sensor_data = pd.read_csv('SensorData_Request.csv'); 
    # Log-in request
    login_response = requests.request(
        "POST",
        "https://qsense.noolitic.com/api/v2/login",
        json={
            "username": "AlessandroP", 
            "password": "qsenseair!"
            },
        headers={
            "content-type" : "application/json"
            }
        )
    # Success check
    if login_response.status_code == 200:
        print('API log-in SUCCESS', file=redirect)

    else:
        print('API log-in FAILED', file=redirect)
        print('Exiting...', file=redirect)

    #
    token = login_response.json()['token']
    # Use the log-in token to request measurements data
    for i in range(0, len(sensor_data)):#For each sensor in the "SensorData_Request.csv" file, retrieve the measurement data from the web API endpoint, passing the sensor MAC address, start date (which is the sensor installation date), and end date (which is the current date).
        #
        start_date = sensor_data['InstallationDate'][i]
        start_date_unix = sensor_data['InstallationDateUNIX'][i]
        #
        end_date = datetime.now(); 
        end_date_unix = int(time.mktime(end_date.timetuple())); 
        #
        get_response = requests.request(
            "GET",
            "https://qsense.noolitic.com/api/v2/plugins/qsense/customer/datas/"+ sensor_data['SensorMAC'][i] + "?start=" + str(start_date_unix) + "&end=" + str(end_date_unix),
            json={
                "username": "ChristosN", 
                "password": "qsenseair!"
                },
            headers={
                "Content-type" : "application/json",
                "Authorization" : "Bearer " + token
                }
            )
        #
        if get_response.status_code == 200:#If the data retrieval is successful, parse the response JSON object and create a Pandas DataFrame.
            #
            print('...', file=redirect)
            print('Parsing sensor '+str(sensor_data['SensorNo'][i]) + ' data: SUCCESS', file=redirect)
            print('...', file=redirect)
            
        else:
            print('Parsing sensor '+str(sensor_data['SensorNo'][i]) + ' data: FAILED', file=redirect)
        #
        timestamps = json_normalize(get_response.json().get('datas'))
        timestamps['timestamp'] = pd.to_datetime(timestamps['timeStamp'], unit='s'); 
        #
        response = json_normalize(timestamps['values'][0]); cols = list(response['name']); 
        data = pd.DataFrame(timestamps['timestamp']); data[cols]=""; 
        for j in range(0, len(timestamps)):
            for k in range(0, len(cols)):
                data[cols[k]][j] = timestamps['values'][j][k]['value']; 
        #
        data  = data.loc[data['timestamp'] > start_date].sort_values(by=['timestamp'], ascending=True).reset_index(drop=True); #Filter the DataFrame to include only measurements taken after the sensor installation date.
        #
        years = data['timestamp'][:].dt.year.unique()#Split the DataFrame into monthly CSV files, one for each year and month in the data set.
        months = data['timestamp'][:].dt.month.unique()
        #
        data['year'] = data['timestamp'][:].dt.year
        data['month'] = data['timestamp'][:].dt.month
        #
        print('Exporting data...', file=redirect)
        print('...', file=redirect)

        #
        
        for m in range(0, len(years)):
            for n in range(0, len(months)):
                if len(data.loc[(data['year'] == years[m]) & (data['month'] == months[n])]) > 0:
                    exec('S' + str(sensor_data['SensorNo'][i]) + '_' + str(years[m]) + '_' + str(months[n]).zfill(2) + ' = data.loc[(data["year"] == years[m]) & (data["month"] == months[n])]')
                    exec('S' + str(sensor_data['SensorNo'][i]) + '_' + str(years[m]) + '_' + str(months[n]).zfill(2) + '.drop(columns=["year", "month"], inplace=True)')
                    exec('S' + str(sensor_data['SensorNo'][i]) + '_' + str(years[m]) + '_' + str(months[n]).zfill(2) + '.to_csv("S' + str(sensor_data['SensorNo'][i]) + '_' + str(years[m]) + '_' + str(months[n]).zfill(2) + '.csv", index=False)')
                    exec('del S' + str(sensor_data['SensorNo'][i]) + '_' + str(years[m]) + '_' + str(months[n]).zfill(2))
                    print('Exporting monthly data: SUCCESS')
                    textbox.insert( 'Exporting monthly data: SUCCESS\n')

        
        #
        sensor_data['LastUpdate'][i] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sensor_data['LastUpdateUNIX'][i] = int(time.mktime(datetime.now().timetuple()))
    #
    print('...', file=redirect)
    print('Updating sensor data...', file=redirect)
    

    sensor_data.to_csv("SensorData_Request.csv", index=False)

    print('Writing file: SUCCESS', file=redirect)
    print('...', file=redirect)
    #
    del i, j, k, m, n, start_date, start_date_unix, end_date, end_date_unix, get_response, timestamps, response, cols, data, years, months, token, login_response
    #
    print('DONE', file=redirect)


      
def frame_atmo():
    frame_atmo1 = customtkinter.CTkFrame(root,fg_color="transparent", width=50,corner_radius=0)
    frame_atmo1.grid(row=0, column=1, rowspan=4, columnspan=4, sticky="nsew")
    labelstart = customtkinter.CTkLabel(master=frame_atmo1, text="Enter starting date (Y-m-d):")
    labelstart.grid(row=0,column=0, padx=20, pady=10)
    entry_datestart=customtkinter.CTkEntry(frame_atmo1)
    entry_datestart.grid(row=0, column=1, padx=20, pady=10)
    labelend = customtkinter.CTkLabel(master=frame_atmo1, text="Enter end date (Y-m-d):")
    labelend.grid(row=1,column=0, padx=20, pady=10)
    label = customtkinter.CTkLabel(master=frame_atmo1, text="Leave both fields empty to get last available data, keep end date field empty to only get starting date data")
    label.grid(row=1,column=2, padx=20, pady=10)
    entry_dateend=customtkinter.CTkEntry(frame_atmo1)
    entry_dateend.grid(row=1, column=1, padx=20, pady=10)
    label_name = customtkinter.CTkLabel(master=frame_atmo1, text="Enter filename")
    label_name.grid(row=2,column=0, padx=20, pady=10)
    entry_name=customtkinter.CTkEntry(frame_atmo1)
    entry_name.grid(row=2, column=1, padx=20, pady=10)
    
    button_atmo=customtkinter.CTkButton(frame_atmo1, text="Get Data",command = lambda: get_atmo(entry_datestart.get(),entry_dateend.get(),entry_name.get(),frame_atmo1)) 
    button_atmo.grid(row=3, column=1, padx=20, pady=10)

def get_atmo(start, end,name,frame):
    url = "https://api.atmotube.com/api/v1/data"
    params = {
        "api_key": "3837661f-c425-4ed1-a7f2-6315e4161f26",
        "mac": "C6:40:C8:0F:64:B2",
        "offset": 0,
        "limit": 50,
    }
    if end == "":
        params["date"] = start
    elif end !="" and start !="":
        params["start_date"] = start
        params["end_date"] = end

    response = requests.get(url, params=params)
    data = response.json()["data"]["items"]
    df = pd.DataFrame(data).dropna()
    


    df["time"] = pd.to_datetime(df["time"]) # Convert time column to datetime format
    filename = name +'.csv'

    df.to_csv(filename) # Save dataframe to a CSV file
    label = customtkinter.CTkLabel(master=frame, text="Done")
    label.grid(row=4,column=1, padx=20, pady=10)
  
        
def frame_airhor():
    frame_airhor = customtkinter.CTkFrame(root,fg_color="transparent", width=50,corner_radius=0)
    frame_airhor.grid(row=0, column=1, rowspan=4, columnspan=4, sticky="nsew")
    
    label_date = customtkinter.CTkLabel(frame_airhor, text="Enter start date (Y-m-d):")
    label_date.grid(row=0, column=0, padx=20, pady=10)
    
    label_dateend = customtkinter.CTkLabel(frame_airhor, text="Enter end date")
    label_dateend.grid(row=1, column=0, padx=20, pady=10)

    
    entry_date=customtkinter.CTkEntry(frame_airhor)
    entry_date.grid(row=0, column=1, padx=20, pady=10)
    entry_dateend=customtkinter.CTkEntry(frame_airhor)
    entry_dateend.grid(row=1, column=1, padx=20, pady=10)
    
    button_airh=customtkinter.CTkButton(frame_airhor, text="Get Data",command = lambda: downl_airhor(entry_date.get(),entry_dateend.get(),frame_airhor))
    button_airh.grid(row=2, column=1, padx=20, pady=10)

def downl_airhor(start_date,end_date,frame):
    dfs = [] # create an empty list to store dataframes
    
    for date in pd.date_range(start=start_date, end=end_date):
        date = date.strftime('%Y-%m-%d')
        url1 = 'https://archive.sensor.community/'+date+'/'+date+'_sds011_sensor_76355.csv'
        url2 = 'https://archive.sensor.community/'+date+'/'+date+'_bmp280_sensor_76356.csv'
        filename = date+'Airrohrjean.csv'
    
        # Download the CSV files and concatenate them into one dataframe
        response1 = requests.get(url1)
        df1 = pd.read_csv(io.StringIO(response1.content.decode('utf-8')),sep =';')
        df1 = df1.drop(['sensor_id', 'sensor_type', 'location', 'lat', 'lon','durP1','durP2', 'ratioP1','ratioP2'], axis=1)
    
        response2 = requests.get(url2)
        df2 = pd.read_csv(io.StringIO(response2.content.decode('utf-8')),sep =';')
        df2 = df2.drop(['sensor_id','pressure_sealevel','altitude', 'sensor_type', 'location', 'lat', 'lon'], axis=1)
    
        df1['Timestamp'] = pd.to_datetime(df1['timestamp'], format='%Y/%m/%d %H:%M:%S').dt.round('min').dropna()
        df1 = df1.set_index('Timestamp').reset_index()
        df1 = df1.drop(['timestamp'],axis=1)
        df2['Timestamp'] = pd.to_datetime(df2['timestamp'], format='%Y/%m/%d %H:%M:%S').dt.round('min').dropna()
        df2 = df2.set_index('Timestamp').reset_index()
        df2 = df2.drop(['timestamp'],axis=1)
    
        # Create sample dataframe with range index
        merged_df = pd.merge_asof(df1, df2, on='Timestamp', direction='nearest')
        # create a timedelta object for 2 hours
        td = timedelta(hours=2)
        
        # adjust timezone by adding the timedelta object
        merged_df['Timestamp'] = merged_df['Timestamp'] + td
    
        dfs.append(merged_df) # append the merged dataframe to the list
    
    df_final = pd.concat(dfs, ignore_index=True).dropna() # concatenate all dataframes
    df_final.to_csv(filename, index=False) # save the final dataframe as a CSV file
    label = customtkinter.CTkLabel(master=frame, text="Done")
    label.grid(row=4,column=1, padx=20, pady=10)


"Load files"
def load_file():
    destroyFrames()
    
    # Load CSV file into pandas dataframe

    frame_load = customtkinter.CTkFrame(root,fg_color="transparent", width=50,corner_radius=0)
    frame_load.grid(row=0, column=1, rowspan=4, columnspan=4, sticky="nsew")
    #frame_load.grid_rowconfigure(4, weight=1)
    
    file_path = tk.filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    # source_var = tk.StringVar(frame_load)
    # source_var.set("")

    def optionmenu_callback(choice):
        return choice
    source_menu = customtkinter.CTkOptionMenu(frame_load,values=["Atmotube", "Airrohr", "Reference"],command=optionmenu_callback)
    source_menu.grid(row=0, column=0, padx=20, pady=10)
    source_menu.set("Select data source")  # set initial value

    entry_name=customtkinter.CTkEntry(frame_load, placeholder_text="Enter dataframe name")
    entry_name.grid(row=1, column=0, padx=20, pady=10)
    ok_button = customtkinter.CTkButton(frame_load, text="OK",command=lambda: process_data(file_path, source_menu.get(),entry_name.get()))
    ok_button.grid(row=2, column=0, padx=20, pady=(10,200))
    
def process_data(file_path, source, df_name):
    names.append(str(df_name))
    if source == "Atmotube":
        if 'Date' in pd.read_csv(file_path,delimiter=','):
            data = pd.read_csv(file_path,delimiter=',')
            atmo_data = data.copy()
            atmo_data['Timestamp'] = pd.to_datetime(atmo_data['Date'], format='%Y/%m/%d %H:%M:%S')
            atmo_data = atmo_data.drop(['Date'], axis=1)
            atmo_data = atmo_data.drop(['Latitude'], axis=1)
            atmo_data = atmo_data.drop(['Longitude'], axis=1)



            atmo_data = atmo_data.rename(columns={
        'VOC, ppm': 'VOC [ppm]',
        'AQS': 'AQS [-]',
        'Temperature, ˚C': 'Temparature [°C]',
        'Humidity, %': 'Humidity [%]',
        'Pressure, hPa': 'Pressure [hPa]',
        'PM1, ug/m³': 'PM1 [µg/m³]',
        'PM2.5, ug/m³': 'PM2.5 [µg/m³]',
        'PM10, ug/m³': 'PM10 [µg/m³]'})
        elif 'Date (GMT)' in pd.read_csv(file_path,delimiter=';'):
            data = pd.read_csv(file_path,delimiter=';')
            atmo_data = data.copy()
            atmo_data['Timestamp'] = pd.to_datetime(atmo_data['Date (GMT)'], format='%Y/%m/%d %H:%M')
            atmo_data = atmo_data.drop(['Date (GMT)'], axis=1)
            atmo_data = atmo_data.drop(['Latitude'], axis=1)
            atmo_data = atmo_data.drop(['Longitude'], axis=1)

            atmo_data = atmo_data.rename(columns={
        'VOC (ppm)': 'VOC [ppm]',
        'Temperature (C)': 'Temparature [°C]',
        'Humidity (%)': 'Humidity [%]',
        'Pressure (mbar)': 'Pressure [hPa]',
        'PM1 (ug/m3)': 'PM1 [µg/m³]',
        'PM2.5 (ug/m3)': 'PM2.5 [µg/m³]',
        'PM10 (ug/m3)': 'PM10 [µg/m³]'})
        elif 'time' in pd.read_csv(file_path,delimiter=';'):
            data = pd.read_csv(file_path,delimiter=';')
            atmo_data = data.copy()
            atmo_data['Timestamp'] = pd.to_datetime(atmo_data['time'], format='%Y/%m/%d %H:%M')
            atmo_data = atmo_data.drop(['time'], axis=1)
            atmo_data = atmo_data.drop(['Latitude'], axis=1)
            atmo_data = atmo_data.drop(['Longitude'], axis=1)

            atmo_data = atmo_data.rename(columns={
        'voc': 'VOC [ppm]',
        't': 'Temparature [°C]',
        'h': 'Humidity [%]',
        'p': 'Pressure [hPa]',
        'pm1': 'PM1 [µg/m³]',
        'pm25': 'PM2.5 [µg/m³]',
        'pm10': 'PM10 [µg/m³]'})            
   
            
        atmo_data = atmo_data.set_index('Timestamp').reset_index()
        data = atmo_data

    
    if source == "Airrohr":
        data = pd.read_csv(file_path, sep=',')
        airh_data = data.copy()
        airh_data['Timestamp'] = pd.to_datetime(airh_data['Timestamp'], format='%Y/%m/%d %H:%M:%S')
        airh_data = airh_data.rename(columns={
            'temperature': 'Temperature [°C]',
            'humidity': 'Humidity [%]',
            'pressure': 'Pressure [hp]',
            'P1': 'PM10 [µg/m³]',
            'P2': 'PM2.5 [µg/m³]'})
        airh_data = airh_data.set_index('Timestamp').reset_index()

        data = airh_data
    if source == "Reference":
        if 'date' in pd.read_csv(file_path,delimiter=';'):
            data = pd.read_csv(file_path,sep = ';')
            ref_data = data.copy()
            ref_data['Timestamp'] = pd.to_datetime(ref_data['date'] + ' ' + ref_data[' heure'], format='%d/%m/%Y %H:%M:%S')
            ref_data = ref_data.drop(['date', ' heure'], axis=1)
            ref_data = ref_data.rename(columns={
        ' "Temperature (°C)"': 'Temperature [°C]',
        ' "Humidite (%)"': 'Humidity [%]',
        ' "Pression (hP)"': 'Pressure [hp]',
        ' "Pm1 (µg/m3)"': 'PM1 [µg/m³]',
        ' "Pm2.5 (µg/m3)"': 'PM2.5 [µg/m³]',
        ' "Pm10 (µg/m3)"': 'PM10 [µg/m³]',
        ' "NO2 (µg/m3)"': 'NO2 [µg/m³]',
        ' "O3 (µg/m3)"': 'O3 [µg/m³]',
        ' "Pluie ()"': 'Rainfall [-]',
        ' "Vitesse (m/s)"': 'Windspeed [m/s]',
        ' "Direction (N) (degrees)"': 'Direction (N) [degrees]'})        
        elif 'timestamp' in pd.read_csv(file_path,delimiter=','):
            data = pd.read_csv(file_path,sep = ',')

            ref_data = data.copy()
            ref_data['Timestamp'] = pd.to_datetime(ref_data['timestamp'], format='%Y/%m/%d %H:%M:%S')
            ref_data = ref_data.drop(['timestamp'], axis=1)
            #ref_data = ref_data.drop(['wind_direction'],axis=1)

            ref_data = ref_data.rename(columns={
        'temperature': 'Temperature [°C]',
        'humidity': 'Humidity [%]',
        'pressure': 'Pressure [hp]',
        'pm1': 'PM1 [µg/m³]',
        'pm25': 'PM2.5 [µg/m³]',
        'pm10': 'PM10 [µg/m³]',
        'no2': 'NO2 [µg/m³]',
        'ozone': 'O3 [µg/m³]',
        'rain': 'Rainfall [-]',
        'wind_speed': 'Windspeed [m/s]'})
        ref_data = ref_data.set_index('Timestamp').reset_index()    
        data = ref_data
    # globals()[df_name] = data
    dataframes[df_name] = data
    #dataframes.append(globals()[df_name])
    print(dataframes)

a = []

def frame_selectplot():
    global frameside_plot
    global frameside_over
    global frameside_plot
    destroyFrames()
    
    frameside_plot = customtkinter.CTkFrame(root, fg_color=('dark grey','light grey'),width=50, corner_radius=0)
    frameside_plot.grid(row=2, column=0, sticky="sew")
    def optionmenu_callback(choice):
        #a.clear()
        df = dataframes.get(choice)
        print(df)
        column_listbox.delete(0, tk.END)
        for col in df.columns[1:]:
            column_listbox.insert(tk.END, col)
        print("optionmenu dropdown clicked:", choice)
        a.append(choice)
    df_selector = customtkinter.CTkOptionMenu(frameside_plot,values=list(dataframes.keys()),command=optionmenu_callback)
    df_selector.grid(row=1, column=0, padx=20, pady=10, sticky="s")

    column_listbox = tk.Listbox(frameside_plot, selectmode=tk.MULTIPLE)
    column_listbox.grid(row=2, column=0, padx=20, pady=10, sticky="s")

    plot_button = customtkinter.CTkButton(frameside_plot, text="Plot", command=lambda: plot_selected_dataframe(a[0], column_listbox.curselection()))
    plot_button.grid(row=3, column=0, padx=20, pady=10, sticky="s")


    frameside_plot.rowconfigure((1,2,3), weight=1)


fig = plt.Figure()


def plot_selected_dataframe(df_name, selected_columns):
    global fig
    print('ubhbj')
    print(selected_columns)
    frame_plot1 = customtkinter.CTkFrame(root, fg_color="transparent",width=50)
    frame_plot1.grid(row=0, column=1, rowspan=4, columnspan=4, sticky="nsew")
    frame_plot1.grid_rowconfigure(4, weight=1)
    
    df = dataframes.get(df_name)
    timestamp_col = df.columns[0]
    selected_col_names = [df.columns[i+1] for i in selected_columns]
    num_cols = len(selected_col_names)
    if num_cols == 0:
        return
    num_rows = (num_cols + 1) // 2
    
    # clear the figure
    fig.clf()
    

    
    if num_cols == 1:
        axs = fig.add_subplot(111)
        col_num = df.columns.get_loc(selected_col_names[0])

        col_name = selected_col_names[0]
        dmask_sorted, y_sorted,dmask2_sorted, y2_sorted = outliers(col_num,df)
        if col_name =='PM1 [µg/m³]':
            axs.axhline(y=15, color='yellow')
            axs.axhline(y=35, color='red')
        if col_name =='PM2.5 [µg/m³]':
            axs.axhline(y=20, color='yellow')
            axs.axhline(y=50, color='red')
        if col_name =='PM10 [µg/m³]':
            axs.axhline(y=30, color='yellow')
            axs.axhline(y=75, color='red')
        elif col_name =='VOC [ppm]':
            axs.axhline(y=0.3, color='red')
            axs.axhline(y=1, color='yellow')
        elif col_name =='O3 [µg/m³]':
            axs.axhline(y=120, color='yellow')
        elif col_name =='NO2 [µg/m³]':
            axs.axhline(y=200, color='yellow')
        axs.plot(dmask_sorted, y_sorted, c='b', linewidth=0.5)
        axs.scatter(dmask2_sorted, y2_sorted, c='r',s=5, label='outliers')
        
        #axs.plot(df[timestamp_col], df[selected_col_names[0]], linewidth=0.5)

        axs.set_ylabel(selected_col_names[0])
        axs.set_title(selected_col_names[0])
        axs.set_xlabel(timestamp_col)
        axs.legend()

           
    else:
        if num_cols == 2:
            axs = fig.subplots(1, 2, subplot_kw={'aspect': 'auto'})
            for i, col_name in enumerate(selected_col_names):
                if col_name == timestamp_col:
                    continue
                col_num = df.columns.get_loc(col_name)

                dmask_sorted, y_sorted,dmask2_sorted, y2_sorted = outliers(col_num,df)
                if col_name =='PM1 [µg/m³]':
                    axs[i].axhline(y=15, color='yellow')
                    axs[i].axhline(y=35, color='red')
                if col_name =='PM2.5 [µg/m³]':
                    axs[i].axhline(y=20, color='yellow')
                    axs[i].axhline(y=50, color='red')
                if col_name =='PM10 [µg/m³]':
                    axs[i].axhline(y=30, color='yellow')
                    axs[i].axhline(y=75, color='red')
                elif col_name =='VOC [ppm]':
                    axs[i].axhline(y=0.3, color='red')
                    axs[i].axhline(y=1, color='yellow')
                elif col_name =='O3 [µg/m³]':
                    axs[i].axhline(y=120, color='yellow')
                elif col_name =='NO2 [µg/m³]':
                    axs[i].axhline(y=200, color='yellow')
                axs[i].plot(dmask_sorted, y_sorted, c='b',linewidth=0.5)
                axs[i].scatter(dmask2_sorted, y2_sorted, c='r',s=5, label='outliers')
                
            
                #axs[i].plot(df[timestamp_col], df[col_name], linewidth=0.5)
                axs[i].set_ylabel(col_name)
                axs[i].set_title(col_name)
                axs[i].tick_params(axis='x', rotation=45)
                axs[i].set_xlabel(timestamp_col)
                axs[i].legend()

        else:
            axs = fig.subplots(num_rows, 2, subplot_kw={'aspect': 'auto'})
            for i, col_name in enumerate(selected_col_names):
                if col_name == timestamp_col:
                    continue
                col_num = df.columns.get_loc(col_name)

                dmask_sorted, y_sorted,dmask2_sorted, y2_sorted = outliers(col_num,df)
                row = i // 2
                col = i % 2
                # Plot outliers in red

                axs[row,col].plot(dmask_sorted, y_sorted, c='b', linewidth=0.5)
                axs[row,col].scatter(dmask2_sorted, y2_sorted, c='r',s=5, label='outliers')
                axs[row,col].legend()

                if col_name =='PM1 [µg/m³]':
                    axs[row,col].axhline(y=15, color='yellow')
                    axs[row,col].axhline(y=35, color='red')
                if col_name =='PM2.5 [µg/m³]':
                    axs[row,col].axhline(y=20, color='yellow')
                    axs[row,col].axhline(y=50, color='red')
                if col_name =='PM10 [µg/m³]':
                    axs[row,col].axhline(y=30, color='yellow')
                    axs[row,col].axhline(y=75, color='red')
                elif col_name =='VOC [ppm]':
                    axs[row,col].axhline(y=0.3, color='red')
                    axs[row,col].axhline(y=1, color='yellow')
                elif col_name =='O3 [µg/m³]':
                    axs[row,col].axhline(y=120, color='yellow')
                elif col_name =='NO2 [µg/m³]':
                    axs[row,col].axhline(y=200, color='yellow')

                axs[row,col].set_ylabel(col_name)
                axs[row,col].set_title(col_name)
                axs[row,col].tick_params(axis='x', rotation=45)
                if i == num_cols - 1 or i == num_cols - 2:
                    axs[row,col].set_xlabel(timestamp_col)
                else: axs[row,col].set_xticklabels([])

                if num_cols % 2 == 1:
                    axs[num_cols//2,num_cols%2].set_visible(False)
                

    fig.subplots_adjust(left=0.08, bottom= 0.13, right=0.96, top=0.96, wspace=0.15, hspace=0.75)

    # create a canvas for the updated figure
    canvas = FigureCanvasTkAgg(fig, master=frame_plot1)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # update the toolbar
    toolbar = NavigationToolbar2Tk(canvas, frame_plot1)
    toolbar.update()


def frame_selectplot2():
    global frameside_plot
    global frameside_correl
    global frameside_over

    destroyFrames()
    selected_data = []  # initialize selected_data as an empty list
    frameside_over = customtkinter.CTkFrame(root, fg_color=('dark grey','light grey'),width=50, corner_radius=0)
    frameside_over.grid(row=2, column=0, sticky="sew")
    
    column_listbox = tk.Listbox(frameside_over, selectmode=tk.MULTIPLE)
    column_listbox.grid(row=2, column=0, padx=20, pady=10, sticky="s")

    def optionmenu_callback(choice):
        df = dataframes.get(choice)
        column_listbox.delete(0, tk.END)
        for col in df.columns[1:]:
            column_listbox.insert(tk.END, col)
        overlap[choice] = df.copy()  # add the selected dataframe to overlap
    
    df_selector = customtkinter.CTkOptionMenu(frameside_over,values=list(dataframes.keys()),command=optionmenu_callback)
    df_selector.grid(row=1, column=0, padx=20, pady=10, sticky="s")
    
    plot_button2 = customtkinter.CTkButton(frameside_over, text="add other dataframe", command=lambda: add_other_dataframe())
    plot_button2.grid(row=3, column=0, padx=20, pady=10, sticky="s")
    
    plot_button3 = customtkinter.CTkButton(frameside_over, text="Plot overlap", command=lambda: plot_overlap(selected_data))
    plot_button3.grid(row=4, column=0, padx=20, pady=10, sticky="s")

    def add_other_dataframe():
        nonlocal selected_data  # indicate that we want to update the value of the variable defined in frame_selectplot2
        # save the selected columns for the current dataframe
        selected_columns = column_listbox.curselection()
        selected_columns = [column_listbox.get(idx) for idx in selected_columns]
        selected_dataframe = list(overlap.keys())[-1]  # get the name of the most recent dataframe added to overlap
        df = overlap[selected_dataframe][selected_columns + ['Timestamp']].copy()  # select the columns and make a copy of the dataframe
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])  # convert the Timestamp column to datetime
        selected_data.append(df)  # append the selected dataframe to the list
    
        # reset the list of selected columns and open the frame again
        column_listbox.selection_clear(0, tk.END)
        frameside_over.tkraise()



fig3 = plt.Figure()



def plot_overlap(data):
    global fig3
    fig3.clf()
    destroyFrames()
    frame_plot3 = customtkinter.CTkFrame(root, fg_color="transparent",width=50)
    frame_plot3.grid(row=0, column=1, rowspan=4, columnspan=4, sticky="nsew")
    frame_plot3.grid_rowconfigure(4, weight=1)
    
    if len(data) == 1:
        ax = [fig3.add_subplot(111)]
    else:
        ax = fig3.subplots(len(data), 1)
    for i in range(len(data)):
        data[i].set_index('Timestamp', inplace=True)
        scaler = MinMaxScaler()
        data_norm = data[i].copy()
        #data_norm[:] = scaler.fit_transform(data_norm)

        # Plot each feature (normalized) vs time
        for col in data_norm.columns:
            data_norm[col] = data_norm[col].astype('float64')    
            data_norm.plot(y=col, use_index=True, ax=ax[i],linewidth =0.5 )
            if col =='PM2.5 [µg/m³]':
                ax[i].axhline(y=20, color='yellow')
                ax[i].axhline(y=50, color='red')   
        fig3.subplots_adjust(left=0.08, bottom= 0.13, right=0.96, top=0.96, wspace=0.15, hspace=0.75)

    # create a canvas for the updated figure
    canvas = FigureCanvasTkAgg(fig3, master=frame_plot3)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    # update the toolbar
    toolbar = NavigationToolbar2Tk(canvas, frame_plot3)
    toolbar.update()  




def frame_correlate():
    global frameside_plot
    global frameside_over
    global frameside_correl
    destroyFrames()
    
    
    
    b=[]
    frameside_correl = customtkinter.CTkFrame(root, fg_color=('dark grey','light grey'),width=50, corner_radius=0)
    frameside_correl.grid(row=2, column=0, sticky="sew")
    def optionmenu_callback(choice):
        b.clear()
        b.append(choice)
    df_selector = customtkinter.CTkOptionMenu(frameside_correl,values=list(dataframes.keys()),command=optionmenu_callback)
    df_selector.grid(row=5, column=0, padx=20, pady=10, sticky="s")
    
    plot_button = customtkinter.CTkButton(frameside_correl, text="Correlate", command=lambda: plot_correlation(b[0]))
    plot_button.grid(row=7, column=0, padx=20, pady=10, sticky="s")

fig1 = plt.Figure()

def plot_correlation(data):
    global fig1

    # create a frame to hold the plot
    frame_plot2 = customtkinter.CTkFrame(root, fg_color="transparent", width=50)
    frame_plot2.grid(row=0, column=1, rowspan=4, columnspan=4, sticky="nsew")
    frame_plot2.grid_rowconfigure(4, weight=1)
    data = dataframes[data]
    fig1.clf()
    ax = fig1.add_subplot(111)    
    sns.heatmap(
            data.corr(numeric_only=True), 
            cmap = sns.diverging_palette(220, 10, as_cmap = True),
            square=True, 
            cbar_kws={'shrink':.9 }, 
            ax=ax,
            annot=True, 
            linewidths=0.1,vmax=1.0, linecolor='white',
            annot_kws={'fontsize':12 })
    ax.set_title("Pearson's Correlation Among Features")
    fig1.subplots_adjust(top=0.96,bottom= 0.2)

    # create a canvas for the updated figure
    canvas = FigureCanvasTkAgg(fig1, master=frame_plot2)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # update the toolbar
    toolbar = NavigationToolbar2Tk(canvas, frame_plot2)
    toolbar.update()
    

    
def change_appearance_mode_event2(new_appearance_mode: str):
    customtkinter.set_appearance_mode(new_appearance_mode)



def change_appearance_mode_event(new_appearance_mode: str):
    customtkinter.set_appearance_mode(new_appearance_mode)


def change_scaling_event(new_scaling: str):
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(new_scaling_float)



    
def destroyFrames():
    for frame_name in ['frameside_correl', 'frameside_over', 'frameside_plot']:
        if frame_name in globals():
            globals()[frame_name].destroy()

def outliers(index,data):
    column_names = data.columns
    
    # get shape of data and number of columns
    n_rows, n_cols = data.shape
    
    # initialize D with zeros and same shape as data
    D = np.zeros((n_rows, len(column_names)))
    # fill D with data from columns in column_names list
    for i, col_name in enumerate(column_names):
        D[:,i] = data[col_name]
    
    D0 = (D - np.mean(D, axis=0))/np.std(D, axis=0)

    # Perform PCA
    pca = PCA()
    pca.fit(D0)

    # Compute the PCs and the scores
    A = pca.components_.T
    Z = D0 @ A
    lamda = pca.singular_values_**2 #the eigenvectors are the singular values squared
    def ecdf(pc):
        i_sort = np.argsort(pc)
        pc_sort = pc[i_sort]
        dist_sort = np.arange(1, pc_sort.size+1)/pc_sort.size
        return i_sort, pc_sort, dist_sort

    # We calculate the Mahalanobis distance using PC2
    dm_pc2 = Z[:,index]**2/lamda[index]
    i_sort, pc2_sort, dist_sort = ecdf(dm_pc2)
    threshold = 0.99
    mask = dist_sort > threshold  # this mask operation creates a boolean array that follows the conditions we impose
    
    dmask = pd.to_datetime(D[i_sort[~mask], 0], unit='ns')
    dmask2 = pd.to_datetime(D[i_sort[mask], 0], unit='ns')
    
    sort_idx = np.argsort(dmask)
    dmask_sorted = dmask[sort_idx]
    y_sorted = D[i_sort[~mask], index][sort_idx]

    sort_idx2 = np.argsort(dmask2)
    dmask2_sorted = dmask2[sort_idx2]
    y2_sorted = D[i_sort[mask], index][sort_idx2]
    return dmask_sorted, y_sorted, dmask2_sorted, y2_sorted

        

def RedirectText(text_widget):#Function to redirect the output to a Tkinter Text widget
    
    def write(string):
        #Add text to the end and scroll to the end
        text_widget.insert('end', string)
        text_widget.see('end')
        text_widget.update_idletasks()

    sys.stdout.write = write

if __name__ == "__main__":
    main()
    root.mainloop()