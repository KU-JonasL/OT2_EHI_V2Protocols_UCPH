##########################
### BEST Library build ###
##########################

## Author Jonas Greve Lauritsen
## Adaptation of the BEST library build.

#### Package loading ####
from opentrons import protocol_api
import pandas as pd
from math import *

#### User Input Parameters ###
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


##################################

#### METADATA ####
metadata = {
    'protocolName': 'Protocol BEST Library Build',
    'apiLevel': '2.20',
    'robotType': 'OT-2',    
    'author': 'Jonas Greve Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Automated (BEST) library build of DNA samples (csv-adjusting version). Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}


#### Protocol script ####
def run(protocol: protocol_api.ProtocolContext):

    #### Loading Protocol Runtime Parameters ####
    parsed_data = protocol.params.AdaptorConc.parse_as_csv()
    user_data = pd.DataFrame(parsed_data[1:], columns = parsed_data[0])
    Col_Number = ceil(len(user_data[0])/8)


    #### LABWARE SETUP ####
    ## Smart labware; thermocycler and temperature modules.
    thermo_module = protocol.load_module('thermocyclerModuleV2')
    cold_module = protocol.load_module('temperature module', 9)


    ## Sample Plate (Placed in thermocycler).
    Sample_plate = thermo_module.load_labware('protocol.params.input_plate_type') ## Same plate as sat up for the purification.


    ## Tip racks (4x 10 µL)
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',4)
    tiprack_10_2 = protocol.load_labware('opentrons_96_filtertiprack_10ul',1)
    tiprack_10_3 = protocol.load_labware('opentrons_96_filtertiprack_10ul',2)
    tiprack_10_4 = protocol.load_labware('opentrons_96_filtertiprack_10ul',3)

    ## Mastermix Setup
    cold_plate = cold_module.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    End_Repair_Mix = cold_plate.wells_by_name()["A1"]
    Adaptors_10mM = cold_plate.wells_by_name()["A4"]
    Adaptors_20mM = cold_plate.wells_by_name()["C4"]
    Ligation_Mix = cold_plate.wells_by_name()["A7"]
    Nick_Fill_In_Mix = cold_plate.wells_by_name()["A10"]

    ## Load liquid
    ER = protocol.define_liquid(name = "End Repair Mix", display_color = "#24DE1B")
    Adap10 = protocol.define_liquid(name = "Adaptor 10 mM", display_color = "#E8BF16")
    Adap20 = protocol.define_liquid(name = "Adaptor 10 mM", display_color = "#E8DE16")
    LIG = protocol.define_liquid(name = "Ligation Mix", display_color = "#1B3CDE")
    FI = protocol.define_liquid(name = "Fill In Mix", display_color = "#E80C0C")
    
    End_Repair_Mix.load_liquid(liquid = ER, volume = (5.85*Col_Number*1.1))
    Adaptors_10mM.load_liquid(liquid = Adap10, volume = (1.5*Col_Number*1.1))
    Adaptors_20mM.load_liquid(liquid = Adap20, volume = (1.5*Col_Number*1.1))
    Ligation_Mix.load_liquid(liquid = LIG, volume = (6*Col_Number*1.2))
    Nick_Fill_In_Mix.load_liquid(liquid = FI, volume = (7.5*Col_Number*1.1))


    #### PIPETTE SETUP ####
    m20 = protocol.load_instrument('p20_multi_gen2', mount = 'right', tip_racks = [tiprack_10_1,tiprack_10_2,tiprack_10_3])
    p10 = protocol.load_instrument('p10_single', mount = 'left', tip_racks = [tiprack_10_4])

    
    ## Ligation height setup - to limit viscous solution on the outside of the tips.
    Ligation_height = [1.75, 1.6, 1.45, 1.30, 1.15, 1, 0.85, 0.70, 0.55, 0.4, 0.25, 0.10] ## List with volume height for 12 transfers and descending.
    pos = 12-Col_Number
    Ligation_height = Ligation_height[pos:] ## Removes highest, unused heights.



    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.

    ## Initial activation of Smart Labware. Activate temperature module early in setup to reduce time waste.
    protocol.set_rail_lights(True)
    protocol.comment("STATUS: Activating Modules")


    ## Activating smart modules
    cold_module.set_temperature(10) ## 10 C for the temperature module as it preserves the solutions while can be reached.
    thermo_module.open_lid()
    thermo_module.set_block_temperature(10) ## 10 C to preserve samples and be reached.
    thermo_module.set_lid_temperature(105)



    #### First step - End repair reaction ####
    protocol.comment("STATUS: End Repair Transfer Step Begun")

    ## Transfering End Repair Mix
    for i in range(Col_Number):
        Column= i*8
        m20.transfer(volume = 5.85, source = End_Repair_Mix, dest = Sample_plate.wells()[Column], mix_before = (2,10), mix_after = (5,10), new_tip = 'always', trash = False)


    ## End Repair Incubation
    protocol.comment("STATUS: End Repair Incubation Begun")
    thermo_module.close_lid()
    profile = [
        {'temperature':20, 'hold_time_minutes':30},
        {'temperature':65, 'hold_time_minutes':30}]
    thermo_module.execute_profile(steps = profile, repetitions = 1, block_max_volume = 30)
    thermo_module.set_block_temperature(10) ## Reset to 10 C while working
    thermo_module.open_lid()



    #### Second step - Adaptors and Ligation ####
    protocol.comment("STATUS: Adaptor Transfer Step Begun")

    ## Transferring Adaptors. The adaptor concentration is chosen based on the csv input using conditional logic.
    for i in range(len(user_data)):
        ## User data for adaptor selection
        #SampleNumber;WellPosition;EXBarcode;SampleID;DNAconc;DNAul;Waterul;Adaptor;Notes
        WellPosition = user_data['WellPosition'][i]
        AdaptorConc = int(user_data['Adaptor'][i])
        
        
        p10.pick_up_tip()
	
	
        if AdaptorConc == 10: ## 10 mM adaptor transfer
            p10.transfer(volume = 1.5, source = Adaptors_10mM, dest = Sample_plate.wells_by_name()[WellPosition], mix_before = (2,4), mix_after = (1,10), new_tip = 'never')
            
        if AdaptorConc == 20: ## 20 mM adaptor transfer
            p10.transfer(volume = 1.5, source = Adaptors_20mM, dest = Sample_plate.wells_by_name()[WellPosition], mix_before = (2,4), mix_after = (1,10), new_tip = 'never')

        p10.return_tip()


    ## Transfering Ligation Mix
    protocol.comment("STATUS: Ligation Transfer Step Begun")

    ## Changing flowrate for aspiration & dispension, as PEG4000 is viscous and requires slowed pipetting.
    m20.flow_rate.aspirate = 3 ## µL/s 
    m20.flow_rate.dispense = 3 ## µL/s

    ## Ligation Pipetting
    for i in range(Col_Number):
        ## Aspiration, mixing, and dispersion. Extra delays to allow viscous liquids to aspirate/dispense. Slow movements to limit adhesion.
        Column= i * 8
        m20.pick_up_tip()

        m20.move_to(location = Ligation_Mix.top())
        m20.move_to(location = Ligation_Mix.bottom(z = Ligation_height[i]), speed = 3)
        m20.mix(repetitions = 2, volume = 6, location = Ligation_Mix.bottom(z = Ligation_height[i]))
        m20.aspirate(volume = 6, location = Ligation_Mix.bottom(z = Ligation_height[i]))
        protocol.delay(10)
        m20.move_to(location = Ligation_Mix.top(), speed = 3)

        m20.dispense(volume = 6, location = Sample_plate.wells()[Column])
        m20.mix(repetitions = 3, volume = 10, location = Sample_plate.wells()[Column])
        protocol.delay(5)
        m20.move_to(location = Sample_plate.wells()[Column].top(), speed = 3)

        m20.return_tip()

    ## Ligation Incubation
    protocol.comment("STATUS: Ligation Incubation Step Begun")
    thermo_module.close_lid()
    profile = [
        {'temperature':20, 'hold_time_minutes':30},
        {'temperature':65, 'hold_time_minutes':10}]
    thermo_module.execute_profile(steps = profile, repetitions = 1, block_max_volume = 37.5)
    thermo_module.set_block_temperature(10) ## Reset to 10 C while working
    thermo_module.open_lid()



    ### Third step - Fill-In Reaction ###

    ## Transfering Fill-In reaction mix
    protocol.comment("STATUS: Fill-In Step Begun")

    ## Changing flowrate for aspiration & dispension to default (7.6 µL/s for 20 µL multichannel pipettes).
    m20.flow_rate.aspirate = 7.6 ## µL/s
    m20.flow_rate.dispense = 7.6 ## µL/s

    ## Fill-in Reaction pipetting
    for i in range(Col_Number):
        Column= i*8
        m20.transfer(volume = 7.5, source = Nick_Fill_In_Mix, dest = Sample_plate.wells()[Column], mix_before=(2,10), mix_after=(5,10), new_tip='always', trash = False)

    ## Fill-In Incubation
    protocol.comment("STATUS: Fill-In Incubation Step Begun")
    thermo_module.close_lid()
    profile = [
        {'temperature':65, 'hold_time_minutes':15},
        {'temperature':80, 'hold_time_minutes':15}]
    thermo_module.execute_profile(steps = profile, repetitions = 1, block_max_volume = 45)
    thermo_module.deactivate_lid() ## Turns off lid
    thermo_module.set_block_temperature(10) ## Reset to 10 C while working
    thermo_module.open_lid()


    ### Protocol finished ###
    protocol.set_rail_lights(False)
    protocol.pause("STATUS: Protocol Completed.")

    ## Shuts down modules
    thermo_module.deactivate()
    cold_module.deactivate()
