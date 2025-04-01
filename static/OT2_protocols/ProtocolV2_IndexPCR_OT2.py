####################################
###       Index PCR setup        ###
####################################

## Author Jonas Greve Lauritsen

##################################

#### Package loading ####
from opentrons import protocol_api
from math import *






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
        choices=[{"display_name": "PCRstrip", "value": "opentrons_96_aluminumblock_generic_pcr_strip_200ul"},
        {"display_name": "LVLSXS200", "value": "LVLXSX200_wellplate_200ul"},
        {"display_name": "PCR Plate", "value": "biorad_96_wellplate_200ul_pcr"}],
        default="biorad_96_wellplate_200ul_pcr"
    )

    ## Output plate format
    parameters.add_str(
    variable_name="output_plate_type",
    display_name="Well plate type",
    choices=[{"display_name": "PCR Strips (Aluminumblock)", "value": "opentrons_96_aluminumblock_generic_pcr_strip_200ul"},
        {"display_name": "PCR Plate", "value": "biorad_96_wellplate_200ul_pcr"}],
    default="opentrons_96_aluminumblock_generic_pcr_strip_200ul",
    )


#### Meta Data ####
metadata = {
    'protocolName': 'Protocol Index PCR Setup',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Transfer for Index PCR: Master Mix, Primers Mix, and Sample-library material. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}

#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):


    #### Loading Protocol Runtime Parameters ####
    Col_Number = ceil(protocol.params.sample_count/8)


    #### LABWARE SETUP ####
    ## Samples and sample format (Dilutions done prior)
    Sample_Plate = protocol.load_labware(protocol.params.input_plate_type,1) ## Generic PCR strip should approximate our types. Low volumes could be problematic.
    Sample_Height = 1.0


    ## PCR PCR plate
    Temp_Module_PCR = protocol.load_module('temperature module', 6)
    iPCR_plate = Temp_Module_PCR.load_labware(protocol.params.output_plate_type) ## OBS Generic plate here no PCR strip is uesd here


    ## Primer plate (each well contain both forward and reverse primers)
    Temp_Module_Primer = protocol.load_module('temperature module',7)
    Primer_plate = Temp_Module_Primer.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')


    ## Master Mix
    MasterMix = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', 4) ## MasterMix to be prepared in advance


    ## Tip racks
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',3) ## Sample Transfer
    tiprack_10_2 = protocol.load_labware('opentrons_96_filtertiprack_10ul',2) ## Primer transfer
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5) ## MasterMix


    #### PIPETTE SETUP ####
    ## Loading pipettes
    m20 = protocol.load_instrument('p20_multi_gen2', mount = 'right', tip_racks = [tiprack_10_1,tiprack_10_2])
    m200 = protocol.load_instrument('p300_multi_gen2', mount = 'left',tip_racks = [tiprack_200_1])



    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Index PCR setup begun")
    protocol.set_rail_lights(True)

    ## Activating Tempeature modules
    Temp_Module_PCR.set_temperature(celsius = 10)
    Temp_Module_Primer.set_temperature(celsius = 10)


    #### Transfer MasterMix to the PCR plate ####
    protocol.comment("STATUS: Transfer MasterMix to PCR plate.")

    m200.pick_up_tip()
    for i in range(Col_Number):
        Col = i*8
        
        ## Sets the mastermix column (assuming 200 µL maximum), and transfers the remaning over to next column.
        if i == 0: 
            MMpos = "A1"
        if i == 5: 
            MMpos = "A2"
            m200.transfer(volume = 30, source = MasterMix.wells_by_name()["A1"], dest =MasterMix.wells_by_name()[MMpos], rate = 0.8, new_tip = 'never') ## Transfer leftover- mastermix
        if i == 10: 
            MMpos = "A3"
            m200.transfer(volume = 30, source = MasterMix.wells_by_name()["A2"], dest =MasterMix.wells_by_name()[MMpos], rate = 0.8, new_tip = 'never') ## Transfer leftover- mastermix
        
        m200.transfer(volume = 38, source = MasterMix.wells_by_name()[MMpos], dest = iPCR_plate.wells()[Col].bottom(z = 1.2), mix_before = (2,30), rate = 0.6, blow_out = False, blowout_location = 'source well', new_tip = 'never')
        ## Deep well plates we have less deep bottoms.
    m200.drop_tip()


    #### Primer Transfer ####
    protocol.comment("STATUS: Transfering Index PCR primer.")
    for i in range(Col_Number):
        Col = i*8
        m20.transfer(volume = 2, source = Primer_plate.wells()[Col], dest = iPCR_plate.wells()[Col].bottom(z = 1.2), mix_after = (2,5), rate = 0.6, new_tip = 'Always', trash = False)


    #### Transfer diluted sample-library to index PCR strips - obs for
    protocol.comment("STATUS: Transfering Diluted Samples to Index PCR strips")
    for i in range (Col_Number):
        Col = i*8
        m20.transfer(volume = 10, source = Sample_Plate.wells()[Col].bottom(z = 1.2), dest = iPCR_plate.wells()[Col].bottom(z = 1.2), mix_before = (2,5), mix_after = (2,10), rate = 0.6, new_tip = 'Always', trash = False)


    ## Protocol complete
    protocol.pause("STATUS: Index PCR Setup Finished")
    Temp_Module_PCR.deactivate()
    Temp_Module_Primer.deactivate()
    protocol.set_rail_lights(False)
