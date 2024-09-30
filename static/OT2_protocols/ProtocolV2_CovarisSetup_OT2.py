#################################
### Covaris plate preparation ###
#################################

## Author Jonas Greve Lauritsen
## Automatic preparation of covaris plates based on csv input

##################################

#### Package loading ####
from opentrons import protocol_api
import pandas as pd
from math import *


#### User Input Parameters ###
def add_parameters(parameters):

    ## CSV file load
    parameters.add_csv_file(
        variable_name = "DNAnormalisingwells",
        display_name = "DNA Normalisation File",
        description = "csv file with normalisation information"
    )

    ## First Tip Available 200 uL
    parameters.add_str(
        variable_name = "First_Tip10",
        display_name = "First tip available, P10 tips",
        default = "A1"
    )

    ## First Tip Available 10 uL
    parameters.add_str(
        variable_name = "First_Tip50",
        display_name = "First tip available, P50 tips",
        default = "A1"
    )

    ## Input Format
    parameters.add_str(
        variable_name="input_plate_type",
        display_name="Well plate type",
        choices=[{"display_name": "PCR Strips (Aluminumblock)", "value": "PCRstrip"},
        {"display_name": "LVL XSX 200 tubes (LVL plate)", "value": "LVLXSX200_wellplate_200ul"},
        {"display_name": "PCR Plate", "value": "biorad_96_wellplate_200ul_pcr"}],
        default="biorad_96_wellplate_200ul_pcr",
    )

##################################

#### Meta Data ####
metadata = {
    'protocolName': 'Protocol Automated Covaris Setup',
    'apiLevel': '2.20',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Covaris automated plate prepper with user CSV input. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    #### Loading Protocol Runtime Parameters ####
    parsed_data = protocol.params.DNAnormalisingwells.parse_as_csv()
    user_data = pd.DataFrame(parsed_data[1:], columns = parsed_data[0])


    #### LABWARE SETUP ####
    ## Input Plate - defaults to PCR wellplate
    Input_plate = protocol.load_labware(protocol.params.input_plate_type)
    
    ## Covaris Plate - custom labware
    Covaris_plate = protocol.load_labware('96afatubetpxplate_96_wellplate_200ul', 3) 
        
    ## Water position - if needed you can pause and exchange water as needed.
    Rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',1)
    H2O_1 = Rack.wells_by_name()["A1"]
    H2O_2 = Rack.wells_by_name()["A2"]

    ## Load liquid
    dH2O = protocol.define_liquid(name = "Sterile, Demineralised Water",description = "Green colored water for demo", display_color = "#336CFF")
    H2O.load_liquid(liquid = dH2O, volume = 2000)
    
    ## Tip racks (2x 10 µL, 2x 200 µl)
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',4)
    tiprack_10_2 = protocol.load_labware('opentrons_96_filtertiprack_10ul',7)
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5)
    tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',6)


    #### PIPETTE SETUP ####
    ## Loading pipettes
    p10 = protocol.load_instrument('p10_single', mount='left', tip_racks=[tiprack_10_1,tiprack_10_2])
    p50 = protocol.load_instrument('p50_single', mount='right', tip_racks=[tiprack_200_1,tiprack_200_2])

    ## Setting start tips (based on user input)
    p10.starting_tip = tiprack_10_1.well(protocol.params.First_Tip10)
    p50.starting_tip = tiprack_200_1.well(protocol.params.First_Tip50)


    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Covaris Setup Begun")
    protocol.set_rail_lights(True)

   
    ## Set up counters for upcoming loop
    H2O = H2O_1
    H2O_available = 2000
    

    ## Loop for transfering samples and H2O. The samples are "cherrypicked" samples from the the user input.
    for i in range(len(user_data)):

        ## Find Sample volume and water volume for transfer.
        #SampleNumber;WellPosition;EXBarcode;SampleID;DNAconc;DNAul;Waterul;Adaptor;Notes
        WellPosition = user_data['WellPosition'][i]
        Sample_Input = user_data['DNAul'][i]
        H2O_Input = user_data['Waterul'][i]

        ## If more than 1950 uL has been removed, second tube is used
        if H2O_available < 50:
            H2O = H2O_2
            H2O_available = 2000
        H2O_available = H2O_available - H2O_Input


        #### If the sample input volume is equal or greater to 5 µL, and the water input is lower than 5 µL: ####
        if Sample_Input >= 5 and H2O_Input < 5:

            ## Adding water first if water input volume is greater than 0. ##
            if H2O_Input > 0: # If command prohibits picking up tips and disposing them without a transfer.
                p10.transfer(volume = H2O_Input, source = H2O.bottom(z = 2.0), dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'always', trash = True) #Transfer pick up new tip

            ## Adding sample (to the water).
            p50.transfer(volume = Sample_Input, source = Input_plate.wells_by_name()[WellPosition], dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'Always', Trash = True, mix_after=(3,15), rate = 0.8)


        #### If the sample input volume is equal or greater to 5 µL, and the water input is also equal or greater than 5 µL: ####
        elif Sample_Input >= 5 and H2O_Input >= 5:

            ## Aspirating H2O then sample, and dispense them together into the covaris plate. Both volume are aspirated together to save time.
            p50.pick_up_tip()
            p50.aspirate(volume = H2O_Input, location = H2O.bottom(z = 2.0)) # First pickup
            p50.touch_tip(location = H2O) # Touching the side of the well to remove excess water.
            p50.aspirate(volume = Sample_Input, location = Input_plate.wells_by_name()[WellPosition]) # Second pickup of DNA
            p50.dispense(volume = (Sample_Input+H2O_Input), location = Covaris_plate.wells_by_name()[WellPosition]) # 30 µL dispense to empty completely
            p50.mix(repetitions = 3, volume = 15, location = Covaris_plate.wells_by_name()[WellPosition], rate = 0.8)

            ## Transferring diluted samples to covaris plate
            p50.drop_tip()


        #### If sample input volume is less than 5 µL. (Water input volume is always above 5 µL here) ####
        elif Sample_Input < 5:
            ## Adding sample to the Covaris plate.
            p10.transfer(volume = Sample_Input, source = Input_plate.wells_by_name()[WellPosition], dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'always', trash = True) #µL

            ## Dispensing H2O into the Covaris plate.
            p50.transfer(volume = H2O_Input, source = H2O.bottom(z = 2.0), dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'Always', trash = True, mix_after = (3,15), rate = 0.8) #µL



    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
