"""This file acts as the main module for this script."""

import traceback
import adsk.core
import adsk.fusion
import csv
import os
# import adsk.cam

# Initialize the global variables for the Application and UserInterface objects.
app = adsk.core.Application.get()
ui  = app.userInterface


def run(_context: str):
    """This function is called by Fusion when the script is run."""

    try:
        # Your code goes here.
        design = adsk.fusion.Design.cast(app.activeProduct)

        defaultInputLength = '205'
        Shock_len_Input = ui.inputBox('Input shock length in mm: ', 'Define shock length', defaultInputLength)

        defaultInputStroke = '57'
        Stroke_len_Input = ui.inputBox('Input shock stroke in mm: ', 'Define shock stroke', defaultInputStroke)

        defaultInputWheelDim = 'd129'
        Wheel_Dim_Input = ui.inputBox('Input rear wheel dimension name (eg. d129): ', 'Define dimension name', defaultInputWheelDim)
        
        #ui.messageBox(f'Stroke is = {Stroke_len_Input[0]} and wheel dim name is: {Wheel_Dim_Input[0]}')

        defaultInputFolder = r'Documents/Bike Frame Design/Rate Graphs'
        folderInput = ui.inputBox('Input path to save folder: ', 'Define Save Folder', defaultInputFolder)
        folder = folderInput[0]
        
        #get the name of the parameters
        shock_len = design.allParameters.itemByName('shock_length')

        #shock_start_len = int(shock_len.value)*10
        shock_start_len = int(Shock_len_Input[0])

        #Stroke_len_Input = [55]
        #ui.messageBox(f'Shock len is {shock_start_len} range is {range(0, int(Stroke_len_Input[0]), 5)}')

        #list all sketches in the design
        sketches = design.rootComponent.sketches
        # Iterate through each sketch
        #ui.messageBox(f'{sketches[1].name}')


        #rear axel length is d136
        #d176 is antirise
        #d177 is antisquat
        #d175 is center of gravity

        rear_travel = []
        wheel_path = []
        antirise = []
        antisquat = []
        stroke_travel = []
        step = 1
        shock_len.expression = str(Shock_len_Input[0])
        for shock in range(0, int(Stroke_len_Input[0])+step, step):
            new_len = shock_start_len - shock
            #rear_travel.append(new_len)
            shock_len.expression = str(new_len)
            adsk.doEvents()

            stroke_travel.append(shock)
            sketch_dimensions = sketches[1].sketchDimensions
            for dim in sketch_dimensions:
                if dim.parameter.name == Wheel_Dim_Input[0]:
                    dim_value = float(dim.value)*10
                    rear_travel.append(dim_value)
                if dim.parameter.name == 'd136': #rear axel length dimension
                    dim_value = float(dim.value)*10
                    wheel_path.append(dim_value)
                if dim.parameter.name == 'd175': #centre of gravity dimension
                    dim_value = float(dim.value)*10
                    anti_ref = dim_value
                if dim.parameter.name == 'd176': #antirise dimension
                    dim_value = float(dim.value)*10
                    antirise.append(dim_value)
                if dim.parameter.name == 'd177': #antisquat dimension
                    dim_value = float(dim.value)*10
                    antisquat.append(dim_value)
                else: continue
                

        #write stroke and travel to csv
        filename = os.path.join(os.path.expanduser("~"), folder, 'stroke_travel.csv')
        #ui.messageBox(filename)

        f = open(filename, 'w')

        f.write('stroke,travel,wheel_path,antirise,antisquat\n')
        for i, (stroke, travel, path, rise, squat) in enumerate(zip(stroke_travel, rear_travel, wheel_path, antirise, antisquat)):
            if i == 0:
                continue
            #if stroke == 0:
            #    f.write(f'0,0,0,0,0\n')
            else: f.write(f'{stroke},{travel},{path},{rise/anti_ref},{squat/anti_ref}\n')
        f.close()
        
        for shock in range(int(Stroke_len_Input[0])+step, -step, -1*step):
            
            new_len = shock_start_len - shock
            #rear_travel.append(new_len)
            shock_len.expression = str(new_len)
            adsk.doEvents()

        ui.messageBox(f'Finished. Max travel is {rear_travel[-1]}.')


    except:  #pylint:disable=bare-except
        # Write the error message to the TEXT COMMANDS window.
        app.log(f'Failed:\n{traceback.format_exc()}')
