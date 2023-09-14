import serial
import time
import pandas as pd
import sys
import requests
import os
from datetime import datetime
#Babysitter major limitation: No speed control. Fixed to some random slow value that looks ballpark around 33mm/s

def initComms():
    ser = serial.Serial('COM3', 115200, timeout=1, xonxoff=True)
    #print(ser.name)         # check which port was really used
    time.sleep(1)
    return ser

#This software should open a CSV file, and load the contents of the file into a pandas dataframe
def readCSV(path):
    df = pd.read_csv(path, header=None)
    return df

#Only returns out of this function when line is finished executing
def ExecuteLine(dataframe, linenumber, ser):
    df = dataframe
    line = df.iloc[linenumber]
    line = line.to_numpy()
    if(line[0] == 'Line Start'):
        command = bytes(str('ma ') + str(line[1]) + ',' + str(line[2]) + ',' + str(line[3]) + '\r', 'utf-8')
        ExecuteMovementSafely(command, line, ser)
    if(line[0] == 'Line Passing'):
        command = bytes(str('ma ') + str(line[1]) + ',' + str(line[2]) + ',' + str(line[3]) + '\r', 'utf-8')
        ExecuteMovementSafely(command, line, ser)
    if(line[0] == 'Line End'):
        command = bytes(str('ma ') + str(line[1]) + ',' + str(line[2]) + ',' + str(line[3]) + '\r', 'utf-8')
        ExecuteMovementSafely(command, line, ser)
    if(line[0] == 'Wait Point'):
        time.sleep(line[1])
    if(line[0] == 'Line Speed'):
        command = bytes(str('sp ') + str(line[1]) + '\r', 'utf-8')
        ser.write(command)     # write a string
        recieved = ser.readline()   # read a '\n' terminated line
        if(b'ok' not in recieved):
            print('Something went wrong - Ok not recieved')
            log = open(path_to_log, "a")
            log.write(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ": Something went wrong - Ok not recieved" + "\n")
            log.close()
            exit()
    else:
        return
    
def closeComms(ser):
    ser.close()

def ExecuteMovementSafely(command, dfLine, ser):
    #print(command)
    ser.write(command)     # write a string
    recieved = ser.readline()   # read a '\n' terminated line
    #print(recieved)
    last_recieved = [0,0,0]
    #check that the received line contains the string ok somewhere
    if(b'ok' in recieved):
        target = False
        while target == False:
            ser.write(b'pa\r')     # Poll all axes
            recieved = ser.readline()   # read a '\n' terminated line
            garb = ser.readline()   # read a '\n' terminated line
            #remove the trailing \r\n'
            recieved = recieved[:-2]
            #remove the leading b'
            recieved = recieved.decode("utf-8")
            #split the string into a list
            recieved = recieved.split(',')
            recieved[0] = float(recieved[0])
            recieved[1] = float(recieved[1])
            recieved[2] = float(recieved[2])
            #if((round(recieved[0],2) - round(dfLine[1],2)) < 0.2 and (round(recieved[0],2) - round(dfLine[1],2)) > -0.2 and (round(recieved[1],2) - round(dfLine[2],2)) < 0.2 and (round(recieved[1],2) - round(dfLine[2],2)) > -0.2 and (round(recieved[2],2) - round(dfLine[3],2))) < 0.2 and (round(recieved[2],2) - round(dfLine[3],2)) > -0.2:
            if((recieved[0] == last_recieved[0] and recieved[1] == last_recieved[1] and recieved[2] == last_recieved[2]) and ((round(recieved[0],2) - round(dfLine[1],2)) < 0.2 and (round(recieved[0],2) - round(dfLine[1],2)) > -0.2 and (round(recieved[1],2) - round(dfLine[2],2)) < 0.2 and (round(recieved[1],2) - round(dfLine[2],2)) > -0.2 and (round(recieved[2],2) - round(dfLine[3],2))) < 0.2 and (round(recieved[2],2) - round(dfLine[3],2)) > -0.2):
                target = True
                log = open(path_to_log, "a")
                log.write(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ": Reached target!\n")
                log.close()
                #print('Reached target!')
            else:
                destination = 'Trying to get to ' + str(round(dfLine[1],2)) + ',' + str(round(dfLine[2],2)) + ',' + str(round(dfLine[3],2))
                current = 'Currently at ' + str(round(recieved[0],2)) + ',' + str(round(recieved[1],2)) + ',' + str(round(recieved[2],2))
                #print(destination)
                #print(current)
                log = open(path_to_log, "a")
                log.write(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ": " + destination + "\n")
                log.write(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ": " + current + "\n")
                log.close()
            last_recieved[0] = recieved[0]
            last_recieved[1] = recieved[1]
            last_recieved[2] = recieved[2]
    else:
        #Crash and burn
        print('Something went wrong - Ok not recieved')
        log = open(path_to_log, "a")
        log.write(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ": Something went wrong - Ok not recieved" + "\n")
        log.close()
        exit()
        return False

ser = initComms()
n = len(sys.argv)
if(n != 2):
    print("Error! Please pass a single argument: the path to the print folder")
    exit()
path_to_folder = sys.argv[1]
path_to_folder = path_to_folder + '\\'
path_to_log = path_to_folder + "Log.txt"
path_to_csv = path_to_folder + "FullFile.csv"
folder_name = os.path.dirname(path_to_log)
folder_name = os.path.basename(folder_name)
df = readCSV(path_to_csv)
#print(df)
log = open(path_to_log, "w")
log.write(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ": Started!\n")
log.close()
start_time = str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
for row in range(len(df)):
    log = open(path_to_log, "a")
    log.write(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ": Completion percentage = " + str(row/len(df)*100) + '%\n')
    log.close()
    print(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + "Completion percentage = " + str(row/len(df)*100) + '%' + '\n')
    ExecuteLine(df, row, ser)

try:
    log = open(path_to_log, "a")
    log.write(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ": Completed! Posted to Slack.\n")
    log.close()
    string = "Print job " + folder_name + " started at " + start_time + " was completed successfully at " + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    response = requests.post('https://hooks.slack.com/services/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', json={'text': string})
except:
    print("Unable to post to Slack!")
    log = open(path_to_log, "a")
    log.write(str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ": Completed! Unable to Slack.\n")
    log.close()

closeComms(ser)