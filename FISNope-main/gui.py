## This code is absolute fucking garbage. It was written as fast as humanly possible, to convert a glue dispensing robot into a microarrayer,
## under the assumption that this would be a temporary fix until a new microarrayer was ordered. It's been several months now, and still this robot
## is the life blood of spotting. In other words, if you aren't me, and you are attempting to make any changes to this code, may God have mercy on your soul ##

import PySimpleGUI as sg
import pandas as pd
import numpy as np
from IPython.display import display, HTML
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import errno
import os
import sys
import shutil
import subprocess
import csv
from datetime import datetime
from natsort import natsorted

#As soon as stuff isnt working comment this line out, this is just to handle the deprecated function warnings!#
#import warnings
#warnings.filterwarnings("ignore")

#"Static" variables (User cannot change these in GUI)

#Software version number
software_rev = 1.7
#X distance from the camera center to the pin center
x_distance_pin_center_to_camera_center = 62.81
#Y distance from camera center to pin center
y_distance_pin_center_to_camera_center = -0.63
#Designated "Safe spot", as navigating to 0 (in X, Y, or Z) risks going "out of bounds" and crashing
safe_home = 5
#Designated "Safe height" for between blots to minimize printing time
safe_dab_height = 20
#The approximate size of each part of the robot code file, should be a few hundred less than 4000
approximate_cut_size = 4000-700
#The machine coordinate location right before purging
blow_ready = [5, 180, 45]
#The machine coordinate location during purging
blow_active = [5,191.5,45]
#Spacing between wells on fetch plate
spacing_between_wells = 4.5
#unchanging dabbing parameters:
dab_csv = 'C:\\Users\\454\\SPOT\\DEV\\Dab.csv'
dab_pitch = 0.25
dab_width_x = 60
dab_width_y = 15
dab_total_available = (dab_width_x / dab_pitch) * (dab_width_y / dab_pitch)
max_spots = 30

#"Dynamic" variables (These will be overriden by user selections in GUI)

#Value of speed to travel while holding an oligo
default_line_speed = 33
#Value of speed to travel while not holding an oligo
default_line_speed_fast = 100
#Number of washes
default_washnum = 3
#Time spent depositing oligo on slide
default_time_spent_on_slide = 0.6
#Location of the input CSV file
default_source_input = ''
#The height at which the needle is at its deepest point inside of a well, potentially plus a little extra to push the needle up
default_well_A1_contact_z = 32.5
#The coordinates (not offset!) of the first point (top left) of the array
default_grid_origin = [0,0]
#The coordinates of the center of the 3 measurable points on the 384 well plate
default_measured_P1 = [19.91+x_distance_pin_center_to_camera_center,4.05+y_distance_pin_center_to_camera_center]
default_measured_L1 = [1.81+x_distance_pin_center_to_camera_center,4.13+y_distance_pin_center_to_camera_center]
default_measured_L24 = [2.01+x_distance_pin_center_to_camera_center,107.31+y_distance_pin_center_to_camera_center]
#The name of the holder
default_holder_name = 'MICROSCOPE'
#The name of the mode
default_mode = 'TEST'
#The operator's name
default_operator = 'ERROR?'
#The print name
defauilt_printname = 'ERROR?'
#The purge time
default_blow_time = 2
#The rinse time
default_rinse_time = 5
#The fetch time
default_fetch_time = 5
#The spacing between spots
default_pitch = 0.25
#The x origin of the dab blotter
default_dab_origin_x = 85.90+x_distance_pin_center_to_camera_center
#The y origin of the dab blotter
default_dab_origin_y = 11.90+y_distance_pin_center_to_camera_center
#Whether blotting is enabled or not
default_blotting_enabled = True
#The time spent blotting
default_dab_time = 2
default_dab_height = 30.4
default_dab_number = 40

#"Alternate Default" variables (used for when different GUI settings need different presets)

#The height at which the needle makes contact with a slide, plus a little extra to push the needle up
grid_contact_z_default_microscope = 36
grid_contact_z_default_zion_1 = 32
grid_contact_z_default_zion_20 = 32
grid_contact_z_default_zion_24 = 31

#The origin point of different holders CAMERA SENSED
microscope_slide_holder_origin = [116.53+x_distance_pin_center_to_camera_center, 12.21+y_distance_pin_center_to_camera_center]
zion_slide_holder_origin = [60.59+x_distance_pin_center_to_camera_center, 49.85+y_distance_pin_center_to_camera_center]
zion_20_slide_holder_origin = [50+x_distance_pin_center_to_camera_center, 50+y_distance_pin_center_to_camera_center]
zion_24_slide_holder_origin = [118.46+x_distance_pin_center_to_camera_center, 11.95+y_distance_pin_center_to_camera_center]

#Number of X copies
x_copies_default_microscope = 0
x_copies_default_zion1 = 0
x_copies_default_zion20 = 2
x_copies_default_zion24 = 3

#number of Y copies
y_copies_default_microscope = 0
y_copies_default_zion1 = 0
y_copies_default_zion20 = 4
y_copies_default_zion24 = 5

#copy offset in x direction
x_copy_offset_default_microscope = 0
x_copy_offset_default_zion1 = 0
x_copy_offset_default_zion20 = -20
x_copy_offset_default_zion24 = -15

#copy offset in y direction
y_copy_offset_default_microscope = 0
y_copy_offset_default_zion1 = 0
y_copy_offset_default_zion20 = 20
y_copy_offset_default_zion24 = 15


#Set variables to default values to start with
line_speed = default_line_speed
line_speed_fast = default_line_speed_fast
washnum = default_washnum
time_spent_on_slide = default_time_spent_on_slide
source_input = default_source_input
well_A1_contact_z = default_well_A1_contact_z
grid_origin = default_grid_origin
measured_P1 = default_measured_P1
measured_L1 = default_measured_L1
measured_L24 = default_measured_L24
holder_name = default_holder_name
mode = default_mode
operator = default_operator
printname = defauilt_printname
blow_time = default_blow_time
rinse_time = default_rinse_time
fetch_time = default_fetch_time
pitch = default_pitch

grid_contact_z = grid_contact_z_default_microscope
holder_origin = microscope_slide_holder_origin
xcopies = x_copies_default_microscope
ycopies = y_copies_default_microscope
xcopydist = x_copy_offset_default_microscope
ycopydist = y_copy_offset_default_microscope

dab_origin_x = default_dab_origin_x 
dab_origin_y = default_dab_origin_y
blotting_enabled = default_blotting_enabled
dab_time = default_dab_time
dab_height = default_dab_height
dab_number = default_dab_number

list_of_points = list()
list_of_fluids_at_points = list()

dab_replace_prespot_time = 0.2

#Adds a command to the command list
def write_command(df, command, val1, val2, val3):
    temp = {'Command': command, 'X': val1, 'Y': val2, 'Z': val3}
    df.loc[len(df.index)] = temp 
    return df

def point_raw_using_wait(df, time, x, y, z, fluid):
    global list_of_points
    global list_of_fluids_at_points
    list_of_points.append([x,y])
    list_of_fluids_at_points.append(fluid)
    write_command(df, 'Line Passing', x, y, safe_home)
    write_command(df, 'Line Passing', x, y, z)
    write_command(df, 'Wait Point', time, '', '')
    write_command(df, 'Line Passing', x, y, safe_home)
    return df

def dab_raw_using_wait(df, time, x, y, z):
    write_command(df, 'Line Passing', x, y, safe_dab_height)
    write_command(df, 'Line Passing', x, y, z)
    write_command(df, 'Wait Point', time, '', '')
    write_command(df, 'Line Passing', x, y, safe_dab_height)
    return df

def setup_for_dab_raw_using_wait(df, x, y):
    write_command(df, 'Line Passing', x, y, safe_home)
    return df

def point_relative_to_grid_origin_using_wait(df, time, dot_offset_x, dot_offset_y, z, fluid):
    global list_of_points
    global list_of_fluids_at_points
    list_of_points.append([grid_origin[0]+dot_offset_x,grid_origin[1]+dot_offset_y])
    list_of_fluids_at_points.append(fluid)
    write_command(df, 'Line Passing', grid_origin[0]+dot_offset_x, grid_origin[1]+dot_offset_y, safe_home)
    write_command(df, 'Line Passing', grid_origin[0]+dot_offset_x, grid_origin[1]+dot_offset_y, z)
    write_command(df, 'Wait Point', time, '', '')
    write_command(df, 'Line Passing', grid_origin[0]+dot_offset_x, grid_origin[1]+dot_offset_y, safe_home)
    return df

def enable_fast_travel(df):
    write_command(df, 'Line End', safe_home,safe_home,safe_home)
    write_command(df, 'Line Speed', line_speed_fast, '', '')
    write_command(df, 'Line Start', safe_home,safe_home,safe_home)
    return df

def disable_fast_travel(df):
    write_command(df, 'Line End', safe_home,safe_home,safe_home)
    write_command(df, 'Line Speed', line_speed, '', '')
    write_command(df, 'Line Start', safe_home,safe_home,safe_home)
    return df

def visit_well_using_wait(df, time, well_name, well_offset_map):
    point = well_to_x_y(well_name, well_offset_map)
    write_command(df, 'Line Passing', point[0], point[1], safe_home)
    write_command(df, 'Line Passing', point[0], point[1], well_A1_contact_z)
    write_command(df, 'Wait Point', time, '', '')
    write_command(df, 'Line Passing', point[0], point[1], safe_home)
    return df

def purge_pin(df, time):
    write_command(df, 'Line Passing', blow_ready[0], blow_ready[1], safe_home)
    write_command(df, 'Line Passing', blow_ready[0], blow_ready[1], blow_ready[2])
    write_command(df, 'Line Passing', blow_active[0], blow_active[1], blow_active[2])
    write_command(df, 'Wait Point', time, '', '')
    write_command(df, 'Line Passing', blow_ready[0], blow_ready[1], blow_ready[2])
    write_command(df, 'Line Passing', blow_ready[0], blow_ready[1], safe_home)
    return df

def end_program(df):
    write_command(df, 'Line End', safe_home,safe_home,safe_home)
    write_command(df, 'End Program', '','','')
    return df

#Send a well as a string, ex: A1, get an x,y coordinate back
def well_to_x_y(well, well_offset_map):
    well = list(well)
    #3 total digits
    if(len(well)>2):
        y = int(str(well[1])+str(well[2])) - 1
        x = well[0]
        x = ord(x)-65
        #at this point x is number of wells left of A1, y is number of wells down of A1
        return [well_offset_map.iloc[y,15-x][0], well_offset_map.iloc[y,15-x][1]]
    
    #2 total digits
    else:
        y = int(well[1]) - 1
        x = well[0]
        x = ord(x)-65
        return [well_offset_map.iloc[y,15-x][0], well_offset_map.iloc[y,15-x][1]]

#Send a oligo well as a string, ex: A1, get a list of wells in the wash cycle back as a string, ex: B1, C1, D1, etc
def well_to_wash_wells(oligo_well, num_wash_fluids, mirror_mode):
    if(mirror_mode):
        oligo_well = list(oligo_well)
        if(len(oligo_well)>2):
            letter = str(oligo_well[0])
            number = str(oligo_well[1])+str(oligo_well[2])
            wash_wells = list()
            for i in range(0, num_wash_fluids):
                letter = chr(ord(letter)-1)
                wash_wells.append(letter+number)
        else:
            letter = str(oligo_well[0])
            number = str(oligo_well[1])
            wash_wells = list()
            for i in range(0, num_wash_fluids):
                letter = chr(ord(letter)-1)
                wash_wells.append(letter+number)
        return wash_wells
    else:
        oligo_well = list(oligo_well)
        if(len(oligo_well)>2):
            letter = str(oligo_well[0])
            number = str(oligo_well[1])+str(oligo_well[2])
            wash_wells = list()
            for i in range(0, num_wash_fluids):
                letter = chr(ord(letter)+1)
                wash_wells.append(letter+number)
        else:
            letter = str(oligo_well[0])
            number = str(oligo_well[1])
            wash_wells = list()
            for i in range(0, num_wash_fluids):
                letter = chr(ord(letter)+1)
                wash_wells.append(letter+number)
        return wash_wells

#A dab is an x,y coordinate that the robot will visit to dab a fluid
#This function creates a CSV file that contains a list of all of the available coordinates for dabbing.
#Each available dab location is a row in the CSV file, with the first column being the x coordinate and the second column being the y coordinate
#The CSV file is the variable csv_name
#The list of available dabs is generated in the following way:
#Starting at dab_origin_x, dab_origin_y, the robot will append valid dab coordinates to the csv file, moving to the right each time by spacing_between_dabs, until the dab_origin_x + spacing_between_dabs is larger than dab_origin_x + valid_dabbing_area_x
#Then the function should move down by spacing_between_dabs, and start over again, moving to the right by spacing_between_dabs until the dab_origin_x + spacing_between_dabs is larger than dab_origin_x + valid_dabbing_area_x
#This process repeats until the dab_origin_y + spacing_between_dabs is larger than dab_origin_y + valid_dabbing_area_y, at which point the function should stop
def generate_available_dab_list(csv_name, valid_dabbing_area_x, valid_dabbing_area_y, spacing_between_dabs):
    x = 0
    y = 0
    with open(csv_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        while(y < (valid_dabbing_area_y)):
            while(x > (-1*valid_dabbing_area_x)):
                writer.writerow([x,y])
                x = x - spacing_between_dabs
            y = y + spacing_between_dabs
            x = 0

#This function should take a CSV file and return the number of lines in that file
def get_dab_life(csv_name):
    if(os.path.isfile(csv_name) and os.path.getsize(csv_name) > 0):
        input = pd.read_csv(csv_name, index_col=False, header=None)
        return len(input)
    else:
        return 0

#This function should take a CSV file that contains a list of all of the available coordinates for dabbing, and return the last available dab coordinate. Then 
#it should remove that dab coordinate from the CSV file. If there are no more available dab coordinates, the function should return dab_origin_x, dab_origin_y
def get_and_remove_last_available_dab(csv_name, dab_origin_x, dab_origin_y, spacing_between_dabs):
    if(mode == 'TEST'):
        if(os.path.isfile(os.path.splitext(csv_name)[0]+'_temp.csv') and os.path.getsize(os.path.splitext(csv_name)[0]+'_temp.csv') > 0):
            input = pd.read_csv(os.path.splitext(csv_name)[0]+'_temp.csv', index_col=False, header=None)
            last_dab = input.iloc[-1]
            input = input.drop(input.index[-1])
            input.to_csv(os.path.splitext(csv_name)[0]+'_temp.csv', index=False, header=False)
            last_dab[0] = (last_dab[0]) + dab_origin_x
            last_dab[1] = (last_dab[1]) + dab_origin_y
            return last_dab
        else:
            if(os.path.isfile(csv_name) and os.path.getsize(csv_name) > 0):
                #copy csv_name to csv_name_temp
                shutil.copyfile(csv_name, os.path.splitext(csv_name)[0]+'_temp.csv')
                input = pd.read_csv(os.path.splitext(csv_name)[0]+'_temp.csv', index_col=False, header=None)
                last_dab = input.iloc[-1]
                input = input.drop(input.index[-1])
                input.to_csv(os.path.splitext(csv_name)[0]+'_temp.csv', index=False, header=False)
                last_dab[0] = (last_dab[0]) + dab_origin_x
                last_dab[1] = (last_dab[1]) + dab_origin_y
                return last_dab
            else:
                return [dab_origin_x, dab_origin_y]
    elif(mode == 'PRINT'):
        if(os.path.isfile(csv_name) and os.path.getsize(csv_name) > 0):
            input = pd.read_csv(csv_name, index_col=False, header=None)
            last_dab = input.iloc[-1]
            input = input.drop(input.index[-1])
            input.to_csv(csv_name, index=False, header=False)
            last_dab[0] = (last_dab[0]) + dab_origin_x
            last_dab[1] = (last_dab[1]) + dab_origin_y
            return last_dab
        else:
            return [dab_origin_x, dab_origin_y]
    else:
        return [dab_origin_x, dab_origin_y]

#This function should use dab_raw_using_wait to dab a fluid at a given coordinate
def go_dab_coordinate(df, next_dab, dab_height, dab_time):
    df = dab_raw_using_wait(df, dab_time, next_dab[0], next_dab[1], dab_height)
    #print("Blotting at: " + str(next_dab[0]) + ", " + str(next_dab[1]) + ", " + str(dab_height))
    return df

def CSV_to_point_map(csv_name, point_map):
    #read from CSV
    input = pd.read_csv(csv_name, index_col=False, header=None) 
    unique_wells = np.unique(input[input.columns].values)
    #display(unique_wells)
    unique_wells = natsorted(unique_wells)
    #display(unique_wells)
    point_map = pd.DataFrame(columns=unique_wells)
    point_map = point_map.astype('object')
    for each in unique_wells:
        #display(each)
        mask = input.applymap(lambda x: each == x if isinstance(x,str) else False).to_numpy()
        indices = np.argwhere(mask)
        #display(indices)
        var = 0
        for item in indices:
            #display(item)
            point_map.loc[var,each] = [indices[var][1],indices[var][0]]
            var = var + 1
    #display(point_map)
    return point_map

#So what is a point_map? A point_map is a dataframe object. Each collumn is labeled as a unique oligo's location in the 384 well plate, so for example, A1, A2, A3... Inside of each collumn are rows and rows (or maybe just 1 row if the plotting sequence is all unique oligos) of (a,b) coordinates. Note that these are NOT machine X,Y coordinates, but rather, a coordinate where A represents the number to the right that this dot is in the array, and B represents the number down that this dot is in the array, starting with 1,1 in the top left corner. So the next dot over, regardless of where it actually gets placed, whether 250um pitch or 500um pitch, is 2,1. 

#What about an offset_map? An offset_map is also a dataframe object, and has the same number of rows and collumns that the input CSV file had. This offset_map is full of x,y coordinates, and tells the machine where each dot should be placed in machine coordinates. So for example, the value at INDEX [1,1] corresponds to the X,Y value where the dot 1,1 should be placed

def generate_384_offset_map(offset_map, known_well_list):
    #Okay so known_well_list is a list of 3 x,y points. Index 0 should be the center of well P1,
    #Index 1 should be the center of well L1, Index 2 should be the center of well L24, and
    offset_map = pd.DataFrame(index=range(24),columns=range(16))
    #offset_map = offset_map.astype('object')

    #Compute offsets
    x_direction_x_distance_between_wells = (known_well_list[0][0] - known_well_list[1][0])/(4) #This will be a positive number, should be very close to 4.5
    x_direction_y_distance_between_wells = (known_well_list[0][1] - known_well_list[1][1])/(4) #This will be a positive or negative number, should be very small
    
    y_direction_x_distance_between_wells = (known_well_list[2][0] - known_well_list[1][0])/(23) #This will be a positive or negative number, should be very small
    y_direction_y_distance_between_wells = (known_well_list[2][1] - known_well_list[1][1])/(23) #This will be a postive number, should be very close to 4.5

    #Manually interpolate A1 well
    virtual_a1 = [(known_well_list[0][0] - (15*x_direction_x_distance_between_wells)),(known_well_list[0][1] - (15*x_direction_y_distance_between_wells))]
    
    r = 0
    for q in reversed(range(0,16)):
        for w in range(0,24):
            offset_map.iloc[w,r] = [virtual_a1[0]+(q*x_direction_x_distance_between_wells)+(w*y_direction_x_distance_between_wells),virtual_a1[1]+(q*x_direction_y_distance_between_wells)+(w*y_direction_y_distance_between_wells)]
        r = r + 1
    return offset_map

def point_map_to_commands(df, point_map, num_wash_fluids, pitch, mirror_mode_enabled, num_x_copies, num_y_copies, x_copy_distance, y_copy_distance, well_offset_map):
    global max_spots

    if(blotting_enabled):
        df = setup_for_dab_raw_using_wait(df, dab_origin_x, dab_origin_y)
        for x in range (0, dab_number):
            df = go_dab_coordinate(df, get_and_remove_last_available_dab(dab_csv, dab_origin_x, dab_origin_y, dab_pitch), dab_height, dab_time)
        df = purge_pin(df, blow_time)

    for (columnName, columnData) in point_map.iteritems():
        if columnName != "Q1":
            #TODO Comment me out to remove bulk printing feature!
            #print("Fetching from well " + columnName)
            df = visit_well_using_wait(df, fetch_time, columnName, well_offset_map)
            df = setup_for_dab_raw_using_wait(df, dab_origin_x, dab_origin_y)
            df = go_dab_coordinate(df, get_and_remove_last_available_dab(dab_csv, dab_origin_x, dab_origin_y, dab_pitch), dab_height, dab_replace_prespot_time)
            remaining_spots = max_spots
            for point in columnData.values:
                if np.isnan(point).any() != True:
                    for x_copy_tracker in range(0, num_x_copies+1):
                        #Comment me back in to remove bulk printing feature
                        #df = visit_well_using_dispense(df, columnName)
                        #print("Placing point with solution from " + columnName)
                        if(remaining_spots > 0):
                            df = point_relative_to_grid_origin_using_wait(df, time_spent_on_slide, -1*(point[0]*pitch)+(x_copy_tracker*x_copy_distance), point[1]*pitch, grid_contact_z, columnName)
                            remaining_spots = remaining_spots - 1
                        else:
                            df = visit_well_using_wait(df, fetch_time, columnName, well_offset_map)
                            df = setup_for_dab_raw_using_wait(df, dab_origin_x, dab_origin_y)
                            df = go_dab_coordinate(df, get_and_remove_last_available_dab(dab_csv, dab_origin_x, dab_origin_y, dab_pitch), dab_height, dab_replace_prespot_time)
                            df = point_relative_to_grid_origin_using_wait(df, time_spent_on_slide, -1*(point[0]*pitch)+(x_copy_tracker*x_copy_distance), point[1]*pitch, grid_contact_z, columnName)
                            remaining_spots = max_spots
                        for y_copy_tracker in range(1, num_y_copies+1):
                            #Comment me back in to remove bulk printing feature
                            #df = visit_well_using_dispense(df, columnName)
                            #print("Placing point with solution from " + columnName)
                            if(remaining_spots > 0):
                                df = point_relative_to_grid_origin_using_wait(df, time_spent_on_slide, -1*(point[0]*pitch)+(x_copy_tracker*x_copy_distance), (point[1]*pitch)+(y_copy_tracker*y_copy_distance), grid_contact_z, columnName)
                                remaining_spots = remaining_spots - 1
                            else:
                                df = visit_well_using_wait(df, fetch_time, columnName, well_offset_map)
                                df = setup_for_dab_raw_using_wait(df, dab_origin_x, dab_origin_y)
                                df = go_dab_coordinate(df, get_and_remove_last_available_dab(dab_csv, dab_origin_x, dab_origin_y, dab_pitch), dab_height, dab_replace_prespot_time)
                                df = point_relative_to_grid_origin_using_wait(df, time_spent_on_slide, -1*(point[0]*pitch)+(x_copy_tracker*x_copy_distance), (point[1]*pitch)+(y_copy_tracker*y_copy_distance), grid_contact_z, columnName)
                                remaining_spots = max_spots
            rinses = well_to_wash_wells(columnName, num_wash_fluids, mirror_mode_enabled)
            #display(rinses)
            df = enable_fast_travel(df)
            for every in rinses:
                #print("Purging pin")
                #df = purge_pin(df, blow_time)
                if(blotting_enabled):
                    df = setup_for_dab_raw_using_wait(df, dab_origin_x, dab_origin_y)
                    for x in range (0, dab_number):
                        df = go_dab_coordinate(df, get_and_remove_last_available_dab(dab_csv, dab_origin_x, dab_origin_y, dab_pitch), dab_height, dab_time)
                #print("Absorbing from wash well " + every)
                df = visit_well_using_wait(df, rinse_time, every, well_offset_map)
            #print("Purging pin")
            if(blotting_enabled):
                df = setup_for_dab_raw_using_wait(df, dab_origin_x, dab_origin_y)
                for x in range (0, dab_number):
                    df = go_dab_coordinate(df, get_and_remove_last_available_dab(dab_csv, dab_origin_x, dab_origin_y, dab_pitch), dab_height, dab_time)
            df = purge_pin(df, blow_time)
            df = disable_fast_travel(df)
    return df

def cut_and_save(df, approximate_cut_size, path):
    #Cutting Code!
    df.to_csv(path+"FullFile.csv", index=False, header=False)
    prev_cut = 0
    counter = 0
    list_of_dfs = list()
    for x in range(0, len(df), approximate_cut_size):
        remaining_to_be_processed = df.iloc[prev_cut:len(df)]
        if len(remaining_to_be_processed) > approximate_cut_size:
            thresh = df.iloc[x+approximate_cut_size:].loc[df['Command'].str.contains("end", case=False)]
            thresh = thresh.index
            thresh = thresh[0]
            temp_df = df.iloc[prev_cut:thresh+1]
            temp_df = write_command(temp_df, 'Call Program', counter+1,'','')
            #temp_df = write_command(temp_df, 'End Program', '','','')
            list_of_dfs.append(temp_df)
            prev_cut=thresh+1
            file_name = 'Part ' + str(counter) + '.csv'
            list_of_dfs[counter].to_csv(path+file_name, index=False, header=False)
        else:
            file_name = 'Part ' + str(counter) + '.csv'
            temp_df = df.iloc[prev_cut:]
            list_of_dfs.append(temp_df)
            list_of_dfs[counter].to_csv(path+file_name, index=False, header=False)
        counter = counter+1
        x = prev_cut+1

def generate_plot_pdfs(path):
    global list_of_points
    global list_of_fluids_at_points
    global holder_name
    math_verify = np.array(list_of_points)
    math_list_of_fluids_at_points = np.array(list_of_fluids_at_points)
    x, y = math_verify.T
    plt.figure()
    plt.scatter(x,y)
    plt.xlim([0, 200])
    plt.ylim([0, 200])
    if(holder_name == 'MICROSCOPE'):
        rect=mpatches.Rectangle((microscope_slide_holder_origin[0], microscope_slide_holder_origin[1]), 76, 26, 90, fill = False, color = "purple", linewidth = 2)
        plt.gca().add_patch(rect)
    if(holder_name == 'ZION1'):
        rect=mpatches.Rectangle((zion_slide_holder_origin[0], zion_slide_holder_origin[1]), 10, 10, 90, fill = False, color = "purple", linewidth = 2)
        plt.gca().add_patch(rect)
    if(holder_name == 'ZION20'):
        for j in range(0,4):
            for k in range(0,5):
                rect=mpatches.Rectangle((zion_20_slide_holder_origin[0]-(20*j), zion_20_slide_holder_origin[1]+(20*k)), 10, 10, 90, fill = False, color = "purple", linewidth = 2)
                plt.gca().add_patch(rect)
    if(holder_name == 'ZION24'):
        for j in range(0,4):
            for k in range(0,6):
                rect=mpatches.Rectangle((zion_24_slide_holder_origin[0]-(15*j), zion_24_slide_holder_origin[1]+(15*k)), 10, 10, 90, fill = False, color = "purple", linewidth = 2)
                plt.gca().add_patch(rect)  
    plt.gca().invert_xaxis()
    plt.gca().invert_yaxis()
    plt.savefig(path+'BuildPlate.pdf')

    if(holder_name == 'MICROSCOPE'):
        plt.xlim([microscope_slide_holder_origin[0], microscope_slide_holder_origin[0]-26])
        plt.ylim([microscope_slide_holder_origin[1]+76, microscope_slide_holder_origin[1]])
    if(holder_name == 'ZION1'):
        plt.xlim([zion_slide_holder_origin[0], zion_slide_holder_origin[0]-10])
        plt.ylim([zion_slide_holder_origin[1]+10, zion_slide_holder_origin[1]])
    if(holder_name == 'ZION20'):
        plt.xlim([zion_20_slide_holder_origin[0], zion_20_slide_holder_origin[0]-100])
        plt.ylim([zion_20_slide_holder_origin[1]+140, zion_20_slide_holder_origin[1]])
    if(holder_name == 'ZION24'):
        plt.xlim([zion_24_slide_holder_origin[0], zion_24_slide_holder_origin[0]-77])
        plt.ylim([zion_24_slide_holder_origin[1]+145, zion_24_slide_holder_origin[1]])
    plt.savefig(path+'Slide.pdf')

    for i, txt in enumerate(math_list_of_fluids_at_points):
        plt.annotate(txt, (x[i], y[i]))
    plt.xlim([grid_origin[0]+.1, grid_origin[0]-3])
    plt.ylim([grid_origin[1]+3, grid_origin[1]-.1])
    plt.savefig(path+'Array.pdf')

colFixtureChoice = sg.Column([
    # Categories sg.Frame
    [sg.Frame('Fixtures:',[[ sg.Radio('Microscope Slide Holder v1', 'radio1', key='-MICROSCOPE-', default=True, enable_events = True, size=(25,1)),
                            sg.Radio('Single Zion Slide Holder v1', 'radio1', key='-ZION1-',  enable_events = True, size=(25,1)),
                            sg.Radio('20x Zion Slide Holder v1', 'radio1', key='-ZION20-',  enable_events = True, size=(25,1)),
                            sg.Radio('24x Zion Slide Holder v1', 'radio1', key='-ZION24-',  enable_events = True, size=(25,1))
                            ]],)]])
colPrintInfo = sg.Column([
    # Information sg.Frame
    [sg.Frame('Print Information:', [
                             [sg.Text('Mode:')],
                             [sg.Radio('Test', 'radio2', default=True, key='-TEST-', size=(10,1)),
                              sg.Radio('Print', 'radio2', key='-PRINT-',  size=(10,1))],
                             [sg.Checkbox('Blotting Enabled', key='-BLOTENABLE-', default=blotting_enabled)],
                             [sg.Text('Operator Name:')],
                             [sg.Input(key='-OPERATORNAME-', size=(19,1))],
                             [sg.Text('Name of Print Job:')],
                             [sg.Input(key='-PRINTNAME-', size=(19,1))],
                             [sg.Text('Notes:')],
                             [sg.Multiline(key='-NOTES-', size=(25,8))]])]])

colPrintParams = sg.Column([
    # Information sg.Frame
    [sg.Frame('Printing Parameters:', [
                             [sg.Text('CSV Input File:')],
                             [sg.Input(key='-INPUT-', size=(19,1)), sg.FileBrowse(size=(10, 1), file_types=(("CSV Files", "*.csv"),))],
                             [sg.Text('Pitch')],
                             [sg.Input(key='-PITCH-', default_text = pitch, size=(19,1)), sg.Text('mm')],
                             [sg.Text('Number of Washes')],
                             [sg.Input(key='-WASHNUM-', default_text = washnum, size=(19,1)), sg.Text('#')],
                             [sg.Text('Robot Travel Speed with Oligo:')],
                             [sg.Input(key='-TRAVELSPEEDWITHOLIGO-', default_text = line_speed, size=(19,1)), sg.Text('mm/s')],
                             [sg.Text('Robot Travel Speed without Oligo:')],
                             [sg.Input(key='-TRAVELSPEEDWITHOUTOLIGO-', default_text = line_speed_fast, size=(19,1)), sg.Text('mm/s')],
                             [sg.Text('Time Spent Depositing On Slide:')],
                             [sg.Input(key='-TIMEONSLIDE-', default_text = time_spent_on_slide, size=(19,1)), sg.Text('s')],
                             [sg.Text('Time Spent Fetching From Well:')],
                             [sg.Input(key='-TIMEINWELL-', default_text = fetch_time, size=(19,1)), sg.Text('s')],
                             [sg.Text('Time Spent Washing in Well:')],
                             [sg.Input(key='-TIMEINWASH-', default_text = rinse_time, size=(19,1)), sg.Text('s')],
                             [sg.Text('Time Spent Purging:')],
                             [sg.Input(key='-BLOWTIME-', default_text = blow_time, size=(19,1)), sg.Text('s')],
                             [sg.Text('Z Height Contacting Slide:')],
                             [sg.Input(key='-DEPTHONSLIDE-', default_text = grid_contact_z, size=(19,1)), sg.Text('Z Value')],
                             [sg.Text('Z Height Fetching From Well:')],
                             [sg.Input(key='-DEPTHINWELL-', default_text = well_A1_contact_z, size=(19,1)), sg.Text('Z Value')],
                              ])]])
colOffsets = sg.Column([
    # Information sg.Frame
    [sg.Frame('Offsets and Calibrations', [
                             [sg.Text('Top Left Corner of First Slide (The top left-most slide in the fixture)')],
                             [sg.Input(key='-HOLDERORIGINX-', default_text = holder_origin[0]-x_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('X Value (+)') , sg.Input(key='-HOLDERORIGINY-', default_text = holder_origin[1]-y_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('Y Value (+)')],
                             [sg.Text('Desired Distance from Top Left Corner of First Slide to Top Left-Most Spot in Grid')],
                             [sg.Input(key='-GRIDOFFSETX-', default_text = '0', size=(9,1)), sg.Text('mm in X (+ / -)'),sg.Input(key='-GRIDOFFSETY-', default_text = '0', size=(9,1)), sg.Text('mm in Y (+ / -)')],
                             [sg.Text('Number of Additional Copies in X Direction')],
                             [sg.Input(key='-XNUMCOPIES-', default_text = xcopies, size=(19,1)), sg.Text('# (+ or 0)')],
                             [sg.Text('Number of Additional Copies in Y Direction')],
                             [sg.Input(key='-YNUMCOPIES-', default_text = ycopies, size=(19,1)), sg.Text('# (+ or 0)')],
                             [sg.Text('Distance To First Additional Copy in X Direction')],
                             [sg.Input(key='-COPYOFFSETX-', default_text = xcopydist, size=(19,1)), sg.Text('mm (+ / 0 / -)')],
                             [sg.Text('Distance To First Additional Copy in Y Direction')],
                             [sg.Input(key='-COPYOFFSETY-', default_text = ycopydist, size=(19,1)), sg.Text('mm (+ / 0 / -)')],
                             [sg.Text('Location of well P1 center')],
                             [sg.Input(key='-P1LOCX-', default_text = measured_P1[0]-x_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('X Value (+)'), sg.Input(key='-P1LOCY-', default_text = measured_P1[1]-y_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('Y Value (+)')],
                             [sg.Text('Location of well L1 center')],
                             [sg.Input(key='-L1LOCX-', default_text = measured_L1[0]-x_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('X Value (+)'), sg.Input(key='-L1LOCY-', default_text = measured_L1[1]-y_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('Y Value (+)')],
                             [sg.Text('Location of well L24 center')],
                             [sg.Input(key='-L24LOCX-', default_text = measured_L24[0]-x_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('X Value (+)'), sg.Input(key='-L24LOCY-', default_text = measured_L24[1]-y_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('Y Value (+)')],
                             ])]])
colActions = sg.Column([[sg.Frame('Actions:',
                            [
                            [sg.Column([[sg.Button('GENERATE') ], [sg.Button('RESET NEW BLOT PAD')]])]],)],
                            [sg.Frame('Blotting Information:',
                            [
                            [sg.Text('Blotter Life Remaining:'), sg.Text(100, key = '-LIFE-'), sg.Text('%')],
                            [sg.ProgressBar(max_value = 100, orientation='h', expand_x=True, size=(20, 20),  key='-PBAR-')],
                            [sg.Text('Top Left Corner of Blotting Pad:')],
                            [sg.Input(key='-BLOTORIGINX-', default_text = dab_origin_x-x_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('X Value (+)') , sg.Input(key='-BLOTORIGINY-', default_text = dab_origin_y-y_distance_pin_center_to_camera_center, size=(9,1)), sg.Text('Y Value (+)')],
                            [sg.Text('Time Spent Blotting:')],
                            [sg.Input(key='-BLOTTIME-', default_text = dab_time, size=(19,1)), sg.Text('s')],
                            [sg.Text('Z Height Contacting Blotting Pad:')],
                            [sg.Input(key='-BLOTHEIGHT-', default_text = dab_height, size=(19,1)), sg.Text('Z Value')],
                            [sg.Text('Number of individual dabs per blotting action:')],
                            [sg.Input(key='-DABNUM-', default_text = dab_number, size=(19,1)), sg.Text('#')],
                            ])]])

layout = [[colFixtureChoice],sg.vtop([colPrintParams,colOffsets,colPrintInfo, colActions])]
window = sg.Window(str('454 Spotter v' + str(software_rev)), layout, resizable=True).Finalize()
window.Maximize()

window['-PBAR-'].update(round((get_dab_life(dab_csv)/dab_total_available)*100,2))
window['-LIFE-'].update(round((get_dab_life(dab_csv)/dab_total_available)*100,2))

while True:
    event, values = window.read()
    if (event == '-MICROSCOPE-') or (event == '-ZION1-') or (event == '-ZION20-') or (event == '-ZION24-'):
        if(values.get('-MICROSCOPE-', False)==True):
            holder_name = 'MICROSCOPE'
            window['-DEPTHONSLIDE-'].update(grid_contact_z_default_microscope)
            window['-HOLDERORIGINX-'].update(microscope_slide_holder_origin[0]-x_distance_pin_center_to_camera_center)
            window['-HOLDERORIGINY-'].update(microscope_slide_holder_origin[1]-y_distance_pin_center_to_camera_center)
            window['-XNUMCOPIES-'].update(x_copies_default_microscope)
            window['-YNUMCOPIES-'].update(y_copies_default_microscope)
            window['-COPYOFFSETX-'].update(x_copy_offset_default_microscope)
            window['-COPYOFFSETY-'].update(y_copy_offset_default_microscope)
        if(values.get('-ZION1-', False)==True):
            holder_name = 'ZION1'
            window['-DEPTHONSLIDE-'].update(grid_contact_z_default_zion_1)
            window['-HOLDERORIGINX-'].update(zion_slide_holder_origin[0]-x_distance_pin_center_to_camera_center)
            window['-HOLDERORIGINY-'].update(zion_slide_holder_origin[1]-y_distance_pin_center_to_camera_center)
            window['-XNUMCOPIES-'].update(x_copies_default_zion1)
            window['-YNUMCOPIES-'].update(y_copies_default_zion1)
            window['-COPYOFFSETX-'].update(x_copy_offset_default_zion1)
            window['-COPYOFFSETY-'].update(y_copy_offset_default_zion1)
        if(values.get('-ZION20-', False)==True):
            holder_name = 'ZION20'
            window['-DEPTHONSLIDE-'].update(grid_contact_z_default_zion_20)
            window['-HOLDERORIGINX-'].update(zion_20_slide_holder_origin[0]-x_distance_pin_center_to_camera_center)
            window['-HOLDERORIGINY-'].update(zion_20_slide_holder_origin[1]-y_distance_pin_center_to_camera_center)
            window['-XNUMCOPIES-'].update(x_copies_default_zion20)
            window['-YNUMCOPIES-'].update(y_copies_default_zion20)
            window['-COPYOFFSETX-'].update(x_copy_offset_default_zion20)
            window['-COPYOFFSETY-'].update(y_copy_offset_default_zion20)
        if(values.get('-ZION24-', False)==True):
            holder_name = 'ZION24'
            window['-DEPTHONSLIDE-'].update(grid_contact_z_default_zion_24)
            window['-HOLDERORIGINX-'].update(zion_24_slide_holder_origin[0]-x_distance_pin_center_to_camera_center)
            window['-HOLDERORIGINY-'].update(zion_24_slide_holder_origin[1]-y_distance_pin_center_to_camera_center)
            window['-XNUMCOPIES-'].update(x_copies_default_zion24)
            window['-YNUMCOPIES-'].update(y_copies_default_zion24)
            window['-COPYOFFSETX-'].update(x_copy_offset_default_zion24)
            window['-COPYOFFSETY-'].update(y_copy_offset_default_zion24)

    if event == 'RESET NEW BLOT PAD':
        dab_origin_x = float(values.get('-BLOTORIGINX-', False)) + x_distance_pin_center_to_camera_center
        dab_origin_y = float(values.get('-BLOTORIGINY-', False)) + y_distance_pin_center_to_camera_center
        dab_time = float(values.get('-BLOTTIME-', False))
        dab_height = float(values.get('-BLOTHEIGHT-', False))
        generate_available_dab_list(dab_csv, dab_width_x, dab_width_y, dab_pitch)
        window['-PBAR-'].update(round((get_dab_life(dab_csv)/dab_total_available)*100,2))
        window['-LIFE-'].update(round((get_dab_life(dab_csv)/dab_total_available)*100,2))

    if event == 'GENERATE':
        line_speed = float(values.get('-TRAVELSPEEDWITHOLIGO-', False))
        line_speed_fast = float(values.get('-TRAVELSPEEDWITHOUTOLIGO-', False))
        time_spent_on_slide = float(values.get('-TIMEONSLIDE-', False))
        fetch_time = float(values.get('-TIMEINWELL-', False))
        blow_time = float(values.get('-BLOWTIME-', False))
        rinse_time = float(values.get('-TIMEINWASH-', False))
        grid_contact_z = float(values.get('-DEPTHONSLIDE-', False))
        well_A1_contact_z = float(values.get('-DEPTHINWELL-', False))
        holder_origin[0] = float(values.get('-HOLDERORIGINX-', False))+x_distance_pin_center_to_camera_center
        holder_origin[1] = float(values.get('-HOLDERORIGINY-', False))+y_distance_pin_center_to_camera_center
        grid_origin[0] = float(values.get('-GRIDOFFSETX-', False)) + float(holder_origin[0])
        grid_origin[1] = float(values.get('-GRIDOFFSETY-', False)) + float(holder_origin[1])
        xcopies = int(values.get('-XNUMCOPIES-', False))
        ycopies = int(values.get('-YNUMCOPIES-', False))
        xcopydist = float(values.get('-COPYOFFSETX-', False))
        ycopydist = float(values.get('-COPYOFFSETY-', False))
        measured_P1 = [float(values.get('-P1LOCX-', False)) + x_distance_pin_center_to_camera_center, float(values.get('-P1LOCY-', False)) + y_distance_pin_center_to_camera_center]
        measured_L1 = [float(values.get('-L1LOCX-', False)) + x_distance_pin_center_to_camera_center, float(values.get('-L1LOCY-', False)) + y_distance_pin_center_to_camera_center]
        measured_L24 = [float(values.get('-L24LOCX-', False)) + x_distance_pin_center_to_camera_center, float(values.get('-L24LOCY-', False)) + y_distance_pin_center_to_camera_center]
        pitch = float(values.get('-PITCH-', False))
        washnum = int(values.get('-WASHNUM-', False))
        source_input = values.get('-INPUT-', False)
        dab_origin_x = float(values.get('-BLOTORIGINX-', False)) + x_distance_pin_center_to_camera_center
        dab_origin_y = float(values.get('-BLOTORIGINY-', False)) + y_distance_pin_center_to_camera_center
        dab_time = float(values.get('-BLOTTIME-', False))
        dab_height = float(values.get('-BLOTHEIGHT-', False))
        dab_number = int(values.get('-DABNUM-', False))

        if(values.get('-TEST-', False) == True):
            mode = 'TEST'
        if(values.get('-PRINT-', False) == True):
            mode = 'PRINT'
        operator = str(values.get('-OPERATORNAME-', False))
        printname = str(values.get('-PRINTNAME-', False))
        notes = str(values.get('-NOTES-', False))
        blotting_enabled = bool(values.get('-BLOTENABLE-', False))
        path = os.path.join(source_input)
        list_of_points = list()
        list_of_fluids_at_points = list()
        #Setup first 3 commands
        dict = {'Command':['Line Speed', 'Point Dispense', 'Line Start'],
                'X':[line_speed, 0.6, safe_home],
                'Y':['', 0.6, safe_home],
                'Z':['','', safe_home]
            }
        df = pd.DataFrame(dict)
        point_map = pd.DataFrame
        original_input_path = path
        point_map = CSV_to_point_map(path, point_map)
        offset_map = pd.DataFrame
        #offset_map = offset_map.astype('object')
        known_well_list = list()
        known_well_list = [[measured_P1[0],measured_P1[1]],[measured_L1[0],measured_L1[1]], [measured_L24[0],measured_L24[1]]]
        well_offset_map = generate_384_offset_map(offset_map, known_well_list)

        df = point_map_to_commands(df, point_map, washnum, pitch, False, xcopies, ycopies, xcopydist,ycopydist, well_offset_map)
        
        df = end_program(df)

        if(mode == 'TEST'):
            path = os.path.join(
            #'C:\\Users\\454\\SPOT\\', 
            #datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            'C:\\Users\\454\\SPOT\\TEST\\', str(datetime.now().strftime('%Y-%m-%d_%H-%M') + "_" + str(operator) + "_" + str(printname)))
        elif(mode == 'PRINT'):
            path = os.path.join(
            #'C:\\Users\\454\\SPOT\\', 
            #datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            'C:\\Users\\454\\SPOT\\PRINT\\', str(datetime.now().strftime('%Y-%m-%d_%H-%M') + "_" + str(operator) + "_" + str(printname)))
        else:
            path = os.path.join(
            #'C:\\Users\\454\\SPOT\\', 
            #datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            'C:\\Users\\454\\SPOT\\ERROR\\', datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        #path = path + "\\"
        path = path + "//"

        params = open(path + "params.txt", "a")  # append mode
        params.write("Print Name: " + str(printname) + " \n")
        params.write("Timestamp: " + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + " \n")
        params.write("Mode: " + str(mode) + "\n")
        params.write("Operator Name: " + str(operator) + "\n")
        params.write("Notes: " + str(notes) + " \n")
        params.write("\n")
        params.write("Software Version: " + str(software_rev) + "\n")
        params.write("\n")
        params.write("Pitch: " + str(pitch) + " mm \n")
        params.write("Number of Washes: " + str(washnum) + " mm \n")
        params.write("Travel Speed While Carrying Oligo: " + str(line_speed) + " mm/s \n")
        params.write("Travel Speed Without Carrying Oligo: " + str(line_speed_fast) + " mm/s \n")
        params.write("Time Spent Depositing on Slide: " + str(time_spent_on_slide) + " s \n")
        params.write("Time Spent Fetching from Well: " + str(fetch_time) + " s \n")
        params.write("Time Spent Spent Purging: " + str(blow_time) + " s \n")
        params.write("Z Height Contacting Slide: " + str(grid_contact_z) + " Z Value \n")
        params.write("Z Height Fetching from Well: " + str(well_A1_contact_z) + " Z Value \n")
        params.write("Top Left Slide Origin X: " + str(float(float(holder_origin[0])-float(x_distance_pin_center_to_camera_center))) + " X Value \n")
        params.write("Top Left Slide Origin Y: " + str(float(float(holder_origin[1])-float(y_distance_pin_center_to_camera_center))) + " Y Value \n")
        params.write("Top Left Grid Point Offset From Origin X: " + str(float(grid_origin[0]) - float(holder_origin[0])) + " mm \n")
        params.write("Top Left Grid Point Offset From Origin Y: " + str(float(grid_origin[1]) - float(holder_origin[1])) + " mm \n")
        params.write("Number of Copies X: " + str(xcopies) + " # \n")
        params.write("Number of Copies Y: " + str(ycopies) + " # \n")
        params.write("Copy Offset X: " + str(xcopydist) + " mm \n")
        params.write("Copy Offset Y: " + str(ycopydist) + " mm \n")
        params.write("Location of Center of P1 Well X Center: " + str(measured_P1[0]-x_distance_pin_center_to_camera_center) + " X Value \n")
        params.write("Location of Center of P1 Well Y Center: " + str(measured_P1[1]-y_distance_pin_center_to_camera_center) + " Y Value \n")
        params.write("Location of Center of L1 Well X Center: " + str(measured_L1[0]-x_distance_pin_center_to_camera_center) + " X Value \n")
        params.write("Location of Center of L1 Well Y Center: " + str(measured_L1[1]-y_distance_pin_center_to_camera_center) + " Y Value \n")
        params.write("Location of Center of L24 Well X Center: " + str(measured_L24[0]-x_distance_pin_center_to_camera_center) + " X Value \n")
        params.write("Location of Center of L24 Well Y Center: " + str(measured_L24[1]-y_distance_pin_center_to_camera_center)+ " Y Value \n")
        params.close()

        shutil.copy(original_input_path, path)

        cut_and_save(df, approximate_cut_size, path)
        generate_plot_pdfs(path)

        #This useful little snippet opens the folder for you!
        path = os.path.realpath(path)
        if sys.platform == "win32":
            os.startfile(path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path])
        

        window['-PBAR-'].update(round((get_dab_life(dab_csv)/dab_total_available)*100,2))
        window['-LIFE-'].update(round((get_dab_life(dab_csv)/dab_total_available)*100,2))

        #Check if the file exists, and if it does, delete it
        if os.path.exists(os.path.splitext(dab_csv)[0]+'_temp.csv'):
            os.remove(os.path.splitext(dab_csv)[0]+'_temp.csv')

        #os.startfile(path)
        #display(len(list_of_dfs))

    #window.refresh()
    if event == sg.WIN_CLOSED:
        break

window.close()
