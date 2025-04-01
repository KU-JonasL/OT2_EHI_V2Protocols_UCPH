#################################
### BEST Library Purification ###
#################################

## Author Jonas Greve Lauritsen
## Automatic preparation of covaris plates based on csv input

############################

#### Package loading ####
from opentrons import protocol_api # type: ignore
from math import *

#### User Input Parameters ###
def add_parameters(parameters):

    ## Number of samples included.
    parameters.add_int(
        variable_name = "sample_count",
        display_name = "Sample count",
        description = "Number of input DNA samples.",
        default = 96,
        minimum = 8,
        maximum = 96
    )

    ## Input Format
    parameters.add_str(
        variable_name="input_plate_type",
        display_name="Well plate type",
        choices=[{"display_name": "Covaris Plate", "value": "96afatubetpxplate_96_wellplate_200ul"},
        {"display_name": "PCR Plate", "value": "biorad_96_wellplate_200ul_pcr"}],
        default="96afatubetpxplate_96_wellplate_200ul"
    )

    ## Output plate format
    parameters.add_str(
    variable_name="output_plate_type",
    display_name="Well plate type",
    choices=[{"display_name": "PCR Strips (Aluminumblock)", "value": "opentrons_96_aluminumblock_generic_pcr_strip_200ul"},
        {"display_name": "LVL XSX 200 tubes (LVL plate)", "value": "LVLXSX200_wellplate_200ul"},
        {"display_name": "PCR Plate", "value": "biorad_96_wellplate_200ul_pcr"}],
    default="biorad_96_wellplate_200ul_pcr",
    )

    ## Off deck incubation
    parameters.add_bool(
        variable_name = "on_deck_incubation",
        display_name = "On-Deck Incubation",
        description = "If true, Script performs an On-deck Incubation.",
        default = True
    )

    ## On deck incubation time
    parameters.add_int(
        variable_name = "incubation_time",
        display_name = "Beads Incubation Time (Mins)",
        description = "Time for incubation of sample and bead mix (in minutes).",
        default = 5,
        minimum = 0,
        maximum = 60
    )

    ## Ethanol volume for wash
    parameters.add_float(
        variable_name = "ethanol_volume",
        display_name = "Ethanol Wash Volume (Per wash)",
        description = "Number of input DNA samples.",
        default = 160,
        minimum = 100,
        maximum = 180
    )

    ## Elution volume
    parameters.add_float(
        variable_name = "elution_volume",
        display_name = "Elution Volume (Per sample)",
        description = "Number of input DNA samples.",
        default = 50,
        minimum = 20,
        maximum = 100
    )

    # ## Elution On-Deck Incubation
    # parameters.add_bool(
    #     variable_name = "elution_incubation",
    #     display_name = "On-Deck Elution Incubation",
    #     description = "If True, the elution-sample mix is incubated on deck.",
    #     default = False
    # )

    # ## Sustainability for high reuse of tip 
    # parameters.add_bool(
    #     variable_name = "sustainaility",
    #     display_name = "Reduced number of Tips",
    #     description = "reduced_tips",
    #     default = False
    # )

##################################


#### Meta Data ####
metadata = {
    'protocolName': 'Protocol BEST Library Purification',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Automated purification of a BEST library build. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}

#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):
   
    #### Loading Protocol Runtime Parameters ####
    Col_Number = ceil(protocol.params.sample_count/8)
    On_Deck_Incubation = protocol.params.on_deck_incubation
    Incubation_Time = protocol.params.incubation_time
    Ethanol_Volume = protocol.params.ethanol_volume
    Elution_Volume = protocol.params.elution_volume
   
    #### LABWARE SETUP ####
    ## Smart labware
    magnet_module = protocol.load_module('magnetic module',4)

    ## Work plates
    Library_plate = magnet_module.load_labware(protocol.params.input_plate_type) ## Input plate
    
    ## Output plate decide from user input. Standard format is PCR plate
    Purified_plate = protocol.load_labware(protocol.params.output_plate_type,10) # Output plate

    ## Purification reservoir and its content.
    Reservoir = protocol.load_labware('deepwellreservoir_12channel_21000ul',1) # Custom labware definition for the 22 mL reservoir
    Beads = Reservoir['A1']
    Ethanol1 = Reservoir['A3']
    Ethanol2 = Reservoir['A4']
    Ebt = Reservoir['A6']

    ## Load Liquid
    


    ## Waste
    Waste1 = Reservoir['A12'] # Beads supernatant waste
    Waste2 = Reservoir['A11'] # 1st ethanol wash waste
    Waste3 = Reservoir['A10'] # 2nd ethanol wash waste


    ## Tip racks
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',6)
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',7)
    tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5)
    tiprack_200_3 = protocol.load_labware('opentrons_96_filtertiprack_200ul',2)
    tiprack_200_4 = protocol.load_labware('opentrons_96_filtertiprack_200ul',3)
    tiprack_200_5 = protocol.load_labware('opentrons_96_filtertiprack_200ul',8)
    tiprack_200_6 = protocol.load_labware('opentrons_96_filtertiprack_200ul',9)


    #### PIPETTE SETUP ####
    ## Loading pipettes
    m200 = protocol.load_instrument('p300_multi_gen2', mount='left', tip_racks=([tiprack_200_1,tiprack_200_2,tiprack_200_3,tiprack_200_4,tiprack_200_5,tiprack_200_6]))
    m20 = protocol.load_instrument('p20_multi_gen2', mount='right', tip_racks=([tiprack_10_1]))


    #### Beads drying time (seconds) ####
    ## Different drying times - Sat from the last removal of the first column. Total drying time is estimated to 4 mins 55 seconds (23s per pipetting cycle)
    BeadsTime = (295, 272, 249, 226, 203, 180, 157, 134, 111, 88, 65, 42)
    BeadsTime = BeadsTime[(Col_Number-1)] # Selecting the relevant drying time


    #### Selecting Reservoir Ethanol height ####
    Ethanol_Height = (31.7,28.9,26.0,23.2,20.3,17.5,14.6,11.8,8.9,6.1,3.2,0.8) 
    pos = 12-Col_Number
    Ethanol_Height = Ethanol_Height[pos:] # Removes highest, unused heights.



    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Purification of BEST Library Build Begun")
    protocol.set_rail_lights(True)
    magnet_module.disengage()


    ## Addition of Magnetic beads - slowed pipette included.
    protocol.comment("STATUS: Beads Transfer Begun")
    for i in range(Col_Number):
        Column = i*8 #Gives the index of the first well in the column
        m200.pick_up_tip()
        m200.move_to(location = Beads.top())
        m200.move_to(location = Beads.bottom(), speed = 40)
        m200.mix(repetitions = 5, volume = 75, location = Beads.bottom())
        m200.aspirate(volume = 75, location = Beads.bottom(), rate = 0.5)
        protocol.delay(5)

        m200.move_to(location = Beads.top(), speed = 10)
        m200.dispense(volume = 75, location = Library_plate.wells()[Column])
        m200.mix(repetitions = 6, volume = 90, location = Library_plate.wells()[Column])
        protocol.delay(5)
        m200.move_to(location = Library_plate.wells()[Column].top(), speed = 40)
        m200.return_tip()

    ## Incubation at room temperature with set temperature
    
    if On_Deck_Incubation == True:
        protocol.comment("STATUS: On-Deck Beads Incubation begun. Plate is incubating for "+ str(Incubation_Time) +"mins")
        protocol.delay(minutes = Incubation_Time)
    elif On_Deck_Incubation == False:
        protocol.pause("ACTION: Seal the Library plate. Spin it down. Run the incunation as intended. You noted "+ str(Incubation_Time) +"mins as you incubation time")


    ## Engaging magnetic module. 5 mins wait for beads attraction
    magnet_module.engage(height_from_base = 10)
    protocol.delay(minutes = 5)

    ## Discarding supernatant.
    protocol.comment("STATUS: Discarding Supernatant")
    for i in range(Col_Number):
        Column = i*8 #Gives the index of the first well in the column
        m200.pick_up_tip()
        m200.transfer(volume = 150, source = Library_plate.wells()[Column].bottom(z = 1.2), dest = Waste1.top(), new_tip = 'never', rate=0.5) #
        m200.air_gap(40,20)
        m200.return_tip()

    ## Double ethanol washing
    protocol.comment("STATUS: Ethanol Wash Begun")
    for k in range(2): # Double wash
        ## Setting up the wash variables
        if k == 0:
            Ethanol_Tips = tiprack_200_3
            Ethanol = Ethanol1
            Waste = Waste2
            protocol.comment("STATUS: First Wash Begun")
        if k == 1:
            Ethanol_Tips = tiprack_200_4
            Ethanol = Ethanol2
            Waste = Waste3
            protocol.comment("STATUS: Second Wash Begun")

        ## Adding Ethanol.
        m200.pick_up_tip(Ethanol_Tips.wells_by_name()['A1']) # Using 1 set of tips for all rows
        m200.mix(repetitions = 3, volume = 200, location = Ethanol.bottom(z = Ethanol_Height[(len(Ethanol_Height)-2)])) # One round of mixing

        for i in range(Col_Number):
            Column = i*8 # Gives the index for the first well in the column
            m200.aspirate(volume = Ethanol_Volume, location = Ethanol.bottom(z = Ethanol_Height[i]), rate = 0.7) 
            m200.dispense(volume = Ethanol_Volume, location = Library_plate.wells()[Column].top(z = 1.2), rate = 1) # Dispenses ethanol from 1.2 mm above the top of the well.
        m200.blow_out(location = Waste) # Blow out to remove potential droplets before returning.
        m200.return_tip()

        ## Removing Ethanol - reusing the tips from above
        for i in range(Col_Number):
            Column = i*8 # Gives the index for the first well in the column
            m200.pick_up_tip(Ethanol_Tips.wells()[Column])
            m200.aspirate(volume = Ethanol_Volume, location = Library_plate.wells()[Column].bottom(z = 1.2), rate = 0.5)
            m200.move_to(location = Library_plate.wells()[Column].top(z=2), speed =100)
            m200.dispense(volume = Ethanol_Volume, location = Waste.top(), rate = 1)
            m200.air_gap(70, 20) #Take in excess/outside droplets to limit cross-contamination.
            m200.return_tip()

    ## Extra ethanol removal step to remove leftover ethanol before drying beads.
    for i in range(Col_Number):
        Column = i*8
        m20.pick_up_tip()
        m20.aspirate(volume = 10, location = Library_plate.wells()[Column].bottom(z = 0.8), rate = 0.6)
        m20.return_tip()


    ## Drying beads (5 mins)
    protocol.comment("STATUS: Drying Beads - time autoadjusted based on number of columns")
    protocol.delay(seconds = BeadsTime) #Times to be verified given m20 step.

    ## Disengaging magnet
    magnet_module.disengage()

    ## Adding EBT buffer.
    protocol.comment("STATUS: EBT Buffer Transfer begun")
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.pick_up_tip()
        m200.transfer(volume = Elution_Volume, source = Ebt, dest = Library_plate.wells()[Column], rate = 1, trash = False , new_tip = 'never', mix_after = (5,20))
        protocol.delay(5)
        m200.move_to(location = Library_plate.wells()[Column].top(), speed = 100)
        m200.return_tip()


    ## Incubation of library plate
    protocol.pause('ACTION: Seal library plate and spin it down shortly. Incubate the library plate for 10 min at 37*C. Press RESUME, when library plate has been returned (without seal) to the magnet module.')

    ## Engaging Magnet. 5 mins wait for beads withdrawal
    magnet_module.engage(height_from_base = 10)
    protocol.delay(minutes = 5)

    ## Transferring purified library to a new plate (purified plate). Transfer is sat higher to remove all.
    protocol.comment("STATUS: Transfer of Purified Library")
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.transfer(volume = Elution_Volume, source = Library_plate.wells()[Column].bottom(z = 1.0), dest = Purified_plate.wells()[Column], new_tip = 'always', trash = False, rate = 0.7)


    ## Deactivating magnet module
    magnet_module.disengage()


    ## Protocol finished
    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
