#################################
### Covaris plate preparation ###
#################################

## Author Jonas Greve Lauritsen & Martí Dalmases
## Automatic Combiner for (up to) 4x 96-well plates for pooling

##################################

#### Package loading ####
from opentrons import protocol_api
import pandas as pd
from math import *

##################################

def add_parameters(parameters):

    ## CSV file load
    #SampleNumber;WellPosition;EXBarcode;SampleID;DNAconc;DNAul;Waterul;Adaptor;Notes
    parameters.add_csv_file(
        variable_name = "PoolSheet",
        display_name = "Pooling sheet",
        description = "csv file with sample pooling details"
    )

    ## Dilution
    parameters.add_bool(
        variable_name = "dilutionchoice",
        display_name = "Dilution",
        description = "If yes, setup includes dilution",
        default = False
    ) 

    ## Input Format
    parameters.add_str(
        variable_name="input_plate_type",
        display_name="Well plate type",
        choices=[{"display_name": "Covaris Plate", "value": "96afatubetpxplate_96_wellplate_200ul"},
        {"display_name": "PCR Plate", "value": "biorad_96_wellplate_200ul_pcr"}],
        default="96afatubetpxplate_96_wellplate_200ul"
    )

    ## Pooltube Format
    parameters.add_str(
        variable_name="pooltube_type",
        display_name="Pooltube type",
        choices=[{"display_name": "1.5 ml tube", "value": "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap"},
        {"display_name": "2 ml tube", "value": "opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap"},
        {"display_name": "5 ml tube", "value": "opentronsrack_15_tuberack_5000ul"}],
        default="opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap"
    )




#### Meta Data ####
metadata = {
    'protocolName': 'Protocol Automated Pool Combiner ',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Automated Combiner for up to 96 pool preparation. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    parsed_data = protocol.params.PoolSheet.parse_as_csv()
    user_data = pd.DataFrame(parsed_data[1:], columns = parsed_data[0])
    DilutionWell = 0

    #### LABWARE SETUP ####
    ## Labware here ##

    ## Pooling tube
    RackType = protocol.load_labware(protocol.params.pooltube_type,3) ## Custom labware for 5mL eppendorf tubes in Opentrons racks.
    PoolTube = RackType.wells_by_name()["A1"]

    ## Input plate 
    SamplePlate = protocol.load_labware(protocol.params.input_plate_type,1)

    ## Dilution plate
    if protocol.params.dilutionchoice is True:
        DilutionPlate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul',2)
        DilutionWater = RackType.wells_by_name()["A2"]

    ## Tip racks
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',4)
    tiprack_10_2 = protocol.load_labware('opentrons_96_filtertiprack_10ul',7)
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5)
    tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',8)


    #### PIPETTE SETUP ####
    ## Loading pipettes
    p10 = protocol.load_instrument('p10_single', mount='left', tip_racks=[tiprack_10_1])
    p50 = protocol.load_instrument('p50_single', mount='right', tip_racks=[tiprack_200_1])

    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.

    protocol.comment("STATUS: Covaris Setup Begun")
    protocol.set_rail_lights(True)



    for i in range(len(user_data)):

        WellPosition = user_data['WellPosition'][i]
        
        if user_data['Dilution'][i] is bool:
            DilutionFactor = user_data['Dilution'][i]
            DilutionVolume = 1
            H2O_Input = 1*(DilutionFactor-1)




        if DilutionFactor > 0:
            DilutionWell = DilutionWell + 1 
            p10.pick_up_tip()
            p10.transfer(volume = H2O_Input, source = DilutionWater, dest = DilutionPlate, new_tip = 'always', trash = False)
            p10
            
            p10.return_tip



    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")