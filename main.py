#TMB - Tibia Mac Bot

#library imports
import os
import subprocess
import re
import importlib
import json
import datetime 

#modules imports
#function to drop unwanted items looted as free account
global drop_module
drop_module = importlib.import_module("drop_function")

#basic sikuli configurations
Settings.ObserveScanRate = 10
Settings.MoveMouseDelay = 0
Settings.ActionLogs = 0

###########################################################
##        #######   ######       #######  ######## ######## 
##       ##     ## ##    ##     ##     ## ##       ##       
##       ##     ## ##           ##     ## ##       ##       
##       ##     ## ##   ####    ##     ## ######   ######   
##       ##     ## ##    ##     ##     ## ##       ##       
##       ##     ## ##    ##     ##     ## ##       ##       
########  #######   ######       #######  ##       ##       
###########################################################

def logoff_function():
    type("3", KeyModifier.CMD + KeyModifier.SHIFT)
    type("l", KeyModifier.CMD)
    print "[TERMINATING EXECUTION]"
    type("c", KeyModifier.CMD + KeyModifier.SHIFT)

#############################################################################################
########  #### ##     ## ######## ##           ######   #######  ##        #######  ########  
##     ##  ##   ##   ##  ##       ##          ##    ## ##     ## ##       ##     ## ##     ## 
##     ##  ##    ## ##   ##       ##          ##       ##     ## ##       ##     ## ##     ## 
########   ##     ###    ######   ##          ##       ##     ## ##       ##     ## ########  
##         ##    ## ##   ##       ##          ##       ##     ## ##       ##     ## ##   ##   
##         ##   ##   ##  ##       ##          ##    ## ##     ## ##       ##     ## ##    ##  
##        #### ##     ## ######## ########     ######   #######  ########  #######  ##     ##
#############################################################################################

#applescript function that returns the color of 1 exact pixel on the screen
def get_pixel_color(posX,posY):   
    command = "screencapture -R"+str(posX)+","+str(posY)+",1,1 -t bmp $TMPDIR/test.bmp && xxd -p -l 3 -s 54 $TMPDIR/test.bmp | sed 's/\\(..\\)\\(..\\)\\(..\\)/\\3\\2\\1/'"
    color = re.sub(r"\s+", "", os.popen(command).read(), flags=re.UNICODE)
    return color

###########################################################################################
##      ##    ###    ##    ## ########   #######  #### ##    ## ######## ######## ########  
##  ##  ##   ## ##    ##  ##  ##     ## ##     ##  ##  ###   ##    ##    ##       ##     ## 
##  ##  ##  ##   ##    ####   ##     ## ##     ##  ##  ####  ##    ##    ##       ##     ## 
##  ##  ## ##     ##    ##    ########  ##     ##  ##  ## ## ##    ##    ######   ########  
##  ##  ## #########    ##    ##        ##     ##  ##  ##  ####    ##    ##       ##   ##   
##  ##  ## ##     ##    ##    ##        ##     ##  ##  ##   ###    ##    ##       ##    ##  
 ###  ###  ##     ##    ##    ##         #######  #### ##    ##    ##    ######## ##     ## 
###########################################################################################

#function to walk to next waypoint
def waypointer(wp):

    print "Walking to [",label,"] waypoint",wp
    
    if label == "hunt":
        action_id = imported_script.label_hunt(wp)
    if label == "leave":
        action_id = imported_script.label_leave(wp)

    #print "Returned action =",action_id
    
    walking_check(0,action_id,wp)
 
    #verifies if should perform some action when reaches destination
    #action_id list:
        #0: indicates its a normal waypoint
        #1: indicates a rope must be used on char's position
        #2: indicates a stair must be used on char's position

    if action_id > 0:waypoint_action(action_id)

#checks for movement related actions
def walking_check(time_stopped,action_id,wp):
    while True:
        #defines the minimap watchable region
        nav = Region(1111,47,110,115)
        nav.onChange(1,changeHandler)
        nav.somethingChanged = False
        nav.observe(1)
        
        #if enters here, means char is still walking
        if nav.somethingChanged:
            
            time_stopped = 0
            
            #verify if it should engage combat while walking
            if action_id == 0 and label == "hunt":
                
                returned_color = get_pixel_color(960,77)
                if returned_color != "3f3f3f":
                    #if enters here, presses Esc to stop my movement
                    type(Key.ESC)
                    #wait half a second
                    wait(0.5)
                    #calls attack function
                    attack_function()
                    #after killing mob, calls back walker function
                    waypointer(wp)
                else: pass
                
            #in case I should NOT engane in combat for some reason
            else: pass
        
        #if nothing changes on the screen for X time, add 1 to stopped timer
        if not nav.somethingChanged:
            time_stopped+=1
            
        if time_stopped == walk_lag_delay:
            break
    
        continue

#sikuli default function to verify if something is changing on screen
def changeHandler(event):
    event.region.somethingChanged = True
    event.region.stopObserver()
    
####################################################################################
##      ## ########        ###     ######  ######## ####  #######  ##    ##  ######  
##  ##  ## ##     ##      ## ##   ##    ##    ##     ##  ##     ## ###   ## ##    ## 
##  ##  ## ##     ##     ##   ##  ##          ##     ##  ##     ## ####  ## ##       
##  ##  ## ########     ##     ## ##          ##     ##  ##     ## ## ## ##  ######  
##  ##  ## ##           ######### ##          ##     ##  ##     ## ##  ####       ## 
##  ##  ## ##           ##     ## ##    ##    ##     ##  ##     ## ##   ### ##    ## 
 ###  ###  ##           ##     ##  ######     ##    ####  #######  ##    ##  ######  
####################################################################################

#tenta subir com corda ou escada
def waypoint_action(action_id): 
    if action_id == 1:
        type(htk_rope)
        click(Location(555,375))
        print "Using rope"
        
    if action_id == 2:
        click(Location(555,375))
        print "Using stairs"

    if action_id == 3:
        type(htk_shovel)
        click(Location(555,375))
        print "Using shovel"
        
    wait(1)
    return  
    
##########################################################################
   ###    ######## ########    ###     ######  ##    ## ######## ########  
  ## ##      ##       ##      ## ##   ##    ## ##   ##  ##       ##     ## 
 ##   ##     ##       ##     ##   ##  ##       ##  ##   ##       ##     ## 
##     ##    ##       ##    ##     ## ##       #####    ######   ########  
#########    ##       ##    ######### ##       ##  ##   ##       ##   ##   
##     ##    ##       ##    ##     ## ##    ## ##   ##  ##       ##    ##  
##     ##    ##       ##    ##     ##  ######  ##    ## ######## ##     ## 
##########################################################################

def attack_function():

    returned_color = get_pixel_color(960,77)
    if returned_color == "3f3f3f": 
        print "battlelist is clear"
        return
    
    else:
        print "monster detected on screen"
        type(Key.SPACE)        
        attacking()
        #wait untill mob is dead to get it's loot
        if take_loot == 1: looter_function()
        #call function again to check if there is another mob on the battlelist
        attack_function()

#function to verify if I am attacking a mob
def attacking():

    #verifies my health and mana situation
    healer_function()
    
    returned_color = get_pixel_color(932,60)
    if (returned_color == 'ff0000' or returned_color == 'ff7f7d'): #red ou white-red
        wait(1)
        attacking()

    if returned_color == 'ffffff': #white
       type(Key.SPACE)
       attacking()
        
    else:return
#

#################################################################
##        #######   #######  ######## ######## ######## ########  
##       ##     ## ##     ##    ##       ##    ##       ##     ## 
##       ##     ## ##     ##    ##       ##    ##       ##     ## 
##       ##     ## ##     ##    ##       ##    ######   ########  
##       ##     ## ##     ##    ##       ##    ##       ##   ##   
##       ##     ## ##     ##    ##       ##    ##       ##    ##  
########  #######   #######     ##       ##    ######## ##     ## 
#################################################################

def looter_function():
    print "looting corpses around char"
    #8 means each click will have KeyModifier.ALT
    click(Location(500,315),8) 
    click(Location(550,315),8)
    click(Location(600,315),8)
    click(Location(600,365),8)
    click(Location(600,415),8)
    click(Location(555,410),8)
    click(Location(500,410),8)
    click(Location(505,365),8)
    click(Location(555,375),8)
    
########################################################    
##     ## ########    ###    ##       ######## ########  
##     ## ##         ## ##   ##       ##       ##     ## 
##     ## ##        ##   ##  ##       ##       ##     ## 
######### ######   ##     ## ##       ######   ########  
##     ## ##       ######### ##       ##       ##   ##   
##     ## ##       ##     ## ##       ##       ##    ##  
##     ## ######## ##     ## ######## ######## ##     ##
########################################################

def healer_function():

    #life checker
    returned_color = get_pixel_color(326,55)
    
    if returned_color == "313131":
        #40% of life - uses potion
        type(htk_life_pot)
    else:
        returned_color = get_pixel_color(460,55)
        if returned_color == "2f2f2f":
            #85% of life - uses spell
            type(htk_life_spell)
        
    #mana checker
    returned_color = get_pixel_color(765,51)    
    if returned_color != '004bb0': type(htk_mana_pot)
        
###########################################################################
########  ######## ########  ##     ## ######## ######## ######## ########  
##     ## ##       ##     ## ##     ## ##       ##       ##       ##     ## 
##     ## ##       ##     ## ##     ## ##       ##       ##       ##     ## 
##     ## ######   ########  ##     ## ######   ######   ######   ########  
##     ## ##       ##     ## ##     ## ##       ##       ##       ##   ##   
##     ## ##       ##     ## ##     ## ##       ##       ##       ##    ##  
########  ######## ########   #######  ##       ##       ######## ##     ##
###########################################################################

def statusBar_check():

    #defines status bar region to reduce search
    statusBar = Region(499,82,106,13)
    
    if statusBar.exists("food.png"):type(htk_food)
    if statusBar.exists("poison.png"):type(htk_heal_poison)
    if equip_ring == 1: equip_ring_checker()
    else: return

#function to equip ring
def equip_ring_checker():

    #defines ring region
    ring_slot = Region(1106,246,45,41)
    
    if ring_slot.exists(Pattern("ring_slot.png").exact()):
        print "equipping ring"
        type(htk_ring)
    else:return

#########################################################################
  ######  ######## ##       ########  ######  ########  #######  ########  
##    ## ##       ##       ##       ##    ##    ##    ##     ## ##     ## 
##       ##       ##       ##       ##          ##    ##     ## ##     ## 
 ######  ######   ##       ######   ##          ##    ##     ## ########  
      ## ##       ##       ##       ##          ##    ##     ## ##   ##   
##    ## ##       ##       ##       ##    ##    ##    ##     ## ##    ##  
 ######  ######## ######## ########  ######     ##     #######  ##     ##
#########################################################################
    
def script_selector_function():
    script_list = (
            "-nothing selected-",
            "[ROOK] Poison Spider",
            "[ROOK] Bear Cave",
            "[EK] Forest Fury v2",
            "[EK] DLair Kazz",
            "[ROOK] Mino Hell v1"
    )
    prompt = select("Please select a script from the list","Available Scripts", options = script_list)

    if prompt == script_list[0]:
        popup("You did not choose a script - Terminating!")
        print "[TERMINATING EXECUTION]"
        type('c', KeyModifier.CMD + KeyModifier.SHIFT)
        
    if prompt == script_list[1]:
        selected_script = "rook_psc"
        script_loader(selected_script)
        
    if prompt == script_list[2]:
        selected_script = "rook_bear"
        script_loader(selected_script)

    if prompt == script_list[3]:
        selected_script = "forest_fury"
        script_loader(selected_script)

    if prompt == script_list[4]:
        selected_script = "dragon_kazz"
        script_loader(selected_script)

    if prompt == script_list[5]:
        selected_script = "rook_mino_hell"
        script_loader(selected_script)

#loads basic configuration from selected script
def script_loader(selected_script):

    global imported_script
    global take_loot
    global drop_items
    global equip_ring
    global last_hunt_wp
    global last_leave_wp
    
    print "Selected Script:",selected_script  
    #imports the script that will be executed on this session
    imported_script = importlib.import_module(selected_script)
           
    #reads the value from the import script
    take_loot = imported_script.take_loot
    #drop_items = imported_script.drop_items
    drop_items = 0
    equip_ring = imported_script.equip_ring
    last_hunt_wp = imported_script.last_hunt_wp
    last_leave_wp = imported_script.last_leave_wp
    
############################################################
 ######   #######  ##    ## ######## ####  ######    ######  
##    ## ##     ## ###   ## ##        ##  ##    ##  ##    ## 
##       ##     ## ####  ## ##        ##  ##        ##       
##       ##     ## ## ## ## ######    ##  ##   ####  ######  
##       ##     ## ##  #### ##        ##  ##    ##        ## 
##    ## ##     ## ##   ### ##        ##  ##    ##  ##    ## 
 ######   #######  ##    ## ##       ####  ######    ######  
############################################################

#hotkey presets
htk_life_pot    = Key.F1
htk_life_spell  = Key.F2
htk_mana_pot    = Key.F3
htk_heal_poison = Key.F10
htk_food        = Key.F12
htk_rope        = "o"
htk_shovel      = "p"
htk_ring        = "l"

#in case ping latency is too high, increase the waiting time
    #1 = low latency, very fast
    #2 or more = medium to high latency
global walk_lag_delay 
walk_lag_delay = 1

#starting waypoint configuration
wp = 1
label = "hunt"

#calls script selector
script_selector_function()
print "[STARTING EXECUTION]"
App.focus("Tibia")

#shows ping on game screen
type(Key.F8, KeyModifier.ALT)

#adjusts minimap zoom (3 + and 1 -)
click(Location(1240,128))
click(Location(1240,128))
click(Location(1240,128))
click(Location(1240,110))

##################################################################
 ######     ###    ##     ## ######## ########   #######  ######## 
##    ##   ## ##   ##     ## ##       ##     ## ##     ##    ##    
##        ##   ##  ##     ## ##       ##     ## ##     ##    ##    
##       ##     ## ##     ## ######   ########  ##     ##    ##    
##       #########  ##   ##  ##       ##     ## ##     ##    ##    
##    ## ##     ##   ## ##   ##       ##     ## ##     ##    ##    
 ######  ##     ##    ###    ######## ########   #######     ##    
##################################################################

while True:

    if label == "hunt":
        attack_function()
        statusBar_check()

        #waypointer
        try: waypointer(wp)
        except:
            print "[ATTENTION] Waypoint",wp,"not found for",label
            pass
    
        #if its the final hunt waypoint
        if wp == last_hunt_wp:
    
            #check if it should drop items
            if drop_items == 1: 
                try: drop_module.dropar(selected_script)
                except: print "Error dropping some of the items";pass
    
            #check if it should leave the hunt
            print "Checking for exit status..."
            label = imported_script.check_exit()
            print "Going",label
    
        wp+=1
        #if it's the last wp, reset
        if wp > last_hunt_wp:
            print "Reseting wp to 1"
            wp = 1

    if label == "leave": 
        
        #waypointer to leave the hunt
        waypointer(wp)
        wp+=1
        
        #if its the final leave waypoint
        if wp > last_leave_wp:
            
            #check if there is battle-on icon
            statusBar = Region(499,82,106,13)
            if statusBar.exists("battleon.png"):
                waitVanish("battleon.png",30)
                logoff_function()
            else: logoff_function()
        
#fim
