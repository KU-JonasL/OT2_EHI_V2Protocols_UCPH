#################################
### Covaris plate preparation ###
#################################

## Author Jonas Greve Lauritsen & Martí Dalmases
## Automatic Combiner for (up to) 4x 96-well plates for pooling

##################################

#### Package loading ####
from opentrons import protocol_api

##################################

def add_parameters(parameters):

    ## CSV file load
    #SampleNumber;WellPosition;EXBarcode;SampleID;DNAconc;DNAul;Waterul;Adaptor;Notes
    parameters.add_csv_file(
        variable_name = "AdaptorConc",
        display_name = "Adaptor Conc Input File",
        description = "csv file with adaptor concentration information"
    )

    ## Input Format
    parameters.add_str(
        variable_name="input_plate_type",
        display_name="Well plate type",
        choices=[{"display_name": "Covaris Plate", "value": "96afatubetpxplate_96_wellplate_200ul"},
        {"display_name": "PCR Plate", "value": "biorad_96_wellplate_200ul_pcr"}],
        default="96afatubetpxplate_96_wellplate_200ul"
    )



#### Meta Data ####
metadata = {
    'protocolName': 'Protocol Automated 4x96 Pool Combiner ',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk> & Martí Dalmases',
    'description': "Automated Combiner for 4x 96 pool preparation. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    #### LABWARE SETUP ####
    
    ## Labware here ##

    PoolTube = protocol.load_labware('opentronsrack_15_tuberack_5000ul',3) ## Custom labware for 5mL eppendorf tubes in Opentrons racks.

    ## Tip racks
    tiprack_10_1 = 1

    tiprack_200_1 = 1


    #### PIPETTE SETUP ####
    ## Loading pipettes
    p20 = protocol.load_instrument('p10_single', mount='left', tip_racks=[tiprack_10_1])
    p50 = protocol.load_instrument('p50_single', mount='right', tip_racks=[tiprack_200_1])


    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Covaris Setup Begun")
    protocol.set_rail_lights(True)


    ## Task: Write a protocol script which combines aspirate volume from each well in 4 different plates to 1 single 5 mL tube (custom labware provided above). Each sample should have 5 µL of its volume transferred. 

    ## Python Protocol API: https://docs.opentrons.com/v2/index.html 

    ## Labware Library: https://labware.opentrons.com/ 

   
    ## Protocol Code here ##


    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
