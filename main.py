#TMB - Tibia Mac Bot

#library imports
import os
import subprocess
import re
import math
import importlib
import json
from datetime import *
from javax.swing import JFrame, JButton, JLabel
from java.awt.BorderLayout import *
from sikuli import *

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
    print "Printing Screen"
    type("3", KeyModifier.CMD + KeyModifier.SHIFT)
    type("l", KeyModifier.CMD)
    print "[TERMINATING EXECUTION]"
    messageCENTER.setText("[END OF EXECUTION]")
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
    messageBOTTOM.setText("Last Analyzed Pixel: "+color)

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
def waypointer(label,wp):

    print "Walking to [",label,"] waypoint",wp
    messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Walking to "+label+" waypoint "+str(wp))
    
    if label == "hunt":
        wp_action = imported_script.label_hunt(wp)
        
    if label == "leave":
        wp_action = imported_script.label_leave(wp)

    #checks if the Char has stopped or continues walking
    walking_check(0,wp_action,label,wp)
    
    return wp_action
 
def walking_check(time_stopped,wp_action,label,wp):
    while time_stopped != walk_lag_delay:
        #defines the minimap watchable region
        nav = Region(1111,47,110,115)
        nav.onChange(1,changeHandler)
        nav.somethingChanged = False
        nav.observe(1)
        
        #if enters here, means char is still walking
        if nav.somethingChanged:
            
            time_stopped = 0
            
            #verifies if it should engage combat while walking
            if label == "hunt" and lure_mode == 0:

                messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Checking battle list while walking...")
                returned_color = get_pixel_color(960,77)
                if returned_color != "3f3f3f": #means there is a mob on battle list
                    #press ESC to stop movement
                    type(Key.ESC)
                    wait(0.5)
                    #calls attack function
                    attack_function()
                    #after killing mob, calls back waypointer function
                    waypointer(label,wp)
                else: pass
                
            #in case shouldn't engane combat
            else: pass
        
        #if nothing changes on the screen for X time, add 1 to stopped timer
        if not nav.somethingChanged:
            time_stopped+=1
            
        #if time_stopped == walk_lag_delay:
            #break
            #return
    
        continue
    else: return

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

#wp_action list:
        #0: indicates its a normal waypoint
        #1: indicates a rope must be used on char's position
        #2: indicates a stair must be used on char's position
        #3: indicates a shovel must be used on char's position

def waypoint_action(wp_action): 
    if wp_action == 1:
        type(htk_rope)
        click(Location(screen_center_x,screen_center_y))
        print "Using rope"
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Using rope")
        
    if wp_action == 2:
        click(Location(screen_center_x,screen_center_y))
        print "Using stairs"
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Using stairs")

    if wp_action == 3:
        type(htk_shovel)
        click(Location(screen_center_x,screen_center_y))
        print "Using shovel"
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Using shovel")

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
        print "Battle list is clear"
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Battlelist is clear, continuing...")
        return
    
    else:
        print "monster detected on screen"
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Monster detected on screen")
        type(Key.SPACE)        
        attacking()
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Mob died")
        #wait untill mob is dead to get it's loot
        if take_loot == 1: melee_looter()
        #call function again to check if there is another mob on the battlelist
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Checking if there is another mob on List")
        attack_function()


#function to verify if attacking a mob
def attacking():

    #verifies my health and mana situation
    messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Checking health and mana")
    healer_function()

    returned_color = get_pixel_color(932,60)
    messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Attacking...")
    if (returned_color == 'ff0000' or returned_color == 'ff7f7d'): #red or whitish-red
        wait(1)
        attacking()

    if returned_color == 'ffffff': #white
       type(Key.SPACE)
       attacking()

    messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Exiting attack loop")
    return


#################################################################
##        #######   #######  ######## ######## ######## ########  
##       ##     ## ##     ##    ##       ##    ##       ##     ## 
##       ##     ## ##     ##    ##       ##    ##       ##     ## 
##       ##     ## ##     ##    ##       ##    ######   ########  
##       ##     ## ##     ##    ##       ##    ##       ##   ##   
##       ##     ## ##     ##    ##       ##    ##       ##    ##  
########  #######   #######     ##       ##    ######## ##     ## 
#################################################################

#MELEE
def melee_looter():
    #1 2 3
    #8 9 4
    #7 6 5
    print "looting corpses around char"
    messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Looting corpses around char")
    click(Location(600,275),8) #1
    click(Location(640,275),8) #2
    click(Location(675,275),8) #3
    click(Location(675,310),8) #4
    click(Location(675,345),8) #5
    click(Location(640,345),8) #6
    click(Location(600,345),8) #7
    click(Location(600,310),8) #8
    click(Location(645,310),8) #9
    
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

    #50% of life - uses potion
    returned_color = get_pixel_color(1172,166)
    if returned_color != "922d2b": type(htk_life_pot)

    #85% of life - uses spell
    returned_color = get_pixel_color(1192,166)
    if returned_color != "922d2b": type(htk_life_spell)
        
    #mana checker
    returned_color = get_pixel_color(1172,179)    
    if returned_color != '2e2893': type(htk_mana_pot)

    return
        
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
    messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Checking debuffs...")

    #defines status bar region to reduce search
    statusBar = Region(499,82,106,13)
    
    if statusBar.exists("food.png"):type(htk_food)
    if statusBar.exists("poison.png"):type(htk_heal_poison)
    if equip_ring == 1: equip_ring_checker()
    return

#function to equip ring
def equip_ring_checker():

    #defines ring region
    ring_slot = Region(1106,246,45,41)
    
    if ring_slot.exists(Pattern("1600737151840.png").exact()):
        print "equipping ring"
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Equipping Ring")
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
            "[RK] Rook PSC",
            "[RK] Rook Mino Hell",
            "[EK] Amazon Camp"
    )
    prompt = select("Please select a script from the list","Available Scripts", options = script_list, default = script_list[0])

    if prompt == script_list[0]:
        popup("You did not choose a script - Terminating!")
        print "[TERMINATING EXECUTION]"
        messageCENTER.setText("[END OF EXECUTION]")
        type('c', KeyModifier.CMD + KeyModifier.SHIFT)
        
    if prompt == script_list[1]:
        selected_script = "rook_psc"
        script_loader(selected_script)

    if prompt == script_list[2]:
        selected_script = "mino_hell"
        script_loader(selected_script)

    if prompt == script_list[3]:
        selected_script = "amazon_camp"
        script_loader(selected_script)

#loads basic configuration from selected script
def script_loader(selected_script):

    global imported_script
    global take_loot
    global lure_mode
    global equip_ring
    global refill_ammo
    global minimap_zoom
    global last_hunt_wp
    global last_leave_wp
    
    print "Selected Script:",selected_script
    #imports the script that will be executed on this session
    imported_script = importlib.import_module(selected_script)
           
    #reads the value from the import script
    combat_mode   = imported_script.combat_mode
    take_loot     = imported_script.take_loot
    lure_mode     = imported_script.lure_mode
    equip_ring    = imported_script.equip_ring
    refill_ammo   = imported_script.refill_ammo
    minimap_zoom  = imported_script.minimap_zoom
    last_hunt_wp  = imported_script.last_hunt_wp
    last_leave_wp = imported_script.last_leave_wp

##########################################################
 #     ## #### ##    ## #### ##     ##    ###    ########  
###   ###  ##  ###   ##  ##  ###   ###   ## ##   ##     ## 
#### ####  ##  ####  ##  ##  #### ####  ##   ##  ##     ## 
## ### ##  ##  ## ## ##  ##  ## ### ## ##     ## ########  
##     ##  ##  ##  ####  ##  ##     ## ######### ##        
##     ##  ##  ##   ###  ##  ##     ## ##     ## ##        
##     ## #### ##    ## #### ##     ## ##     ## ##        
##########################################################

def minimap_adjustment():
    click(Location(1240,128))
    click(Location(1240,128))
    click(Location(1240,128))

    print "adjusting minimap to zoom:",minimap_zoom
    messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Adjusting minimap to zoom: "+str(minimap_zoom))

    if minimap_zoom == 1:
        click(Location(1240,110))

    if minimap_zoom == 2:
        click(Location(1240,110))
        click(Location(1240,110))


###############################################
######## ########     ###    ##     ## ######## 
##       ##     ##   ## ##   ###   ### ##       
##       ##     ##  ##   ##  #### #### ##       
######   ########  ##     ## ## ### ## ######   
##       ##   ##   ######### ##     ## ##       
##       ##    ##  ##     ## ##     ## ##       
##       ##     ## ##     ## ##     ## ######## 
###############################################

#frame structure
frame = JFrame("Console Log")
frame.setLocation(360,630)
frame.setSize(550,140)
frame.visible = True
frame.setAlwaysOnTop(True)
#Sets initial text
messageTOP = JLabel("Current Waypoint: "+label+" "+str(wp))
frame.add(messageTOP,NORTH)
messageBOTTOM = JLabel("")
frame.add(messageBOTTOM,SOUTH)
messageCENTER = JLabel("")
frame.add(messageCENTER,CENTER)
messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"[INITIALIZING BOT]")


############################################################
 ######   #######  ##    ## ######## ####  ######    ######  
##    ## ##     ## ###   ## ##        ##  ##    ##  ##    ## 
##       ##     ## ####  ## ##        ##  ##        ##       
##       ##     ## ## ## ## ######    ##  ##   ####  ######  
##       ##     ## ##  #### ##        ##  ##    ##        ## 
##    ## ##     ## ##   ### ##        ##  ##    ##  ##    ## 
 ######   #######  ##    ## ##       ####  ######    ######  
############################################################

#center of screen
global screen_center_x
global screen_center_y
screen_center_x = 645
screen_center_y = 310

#hotkey presets
htk_life_pot    = Key.F1
htk_life_spell  = "1"
htk_mana_pot    = "3"
htk_heal_poison = Key.F10
htk_food        = Key.F12
htk_rope        = "o"
htk_shovel      = "p"
htk_ring        = "l"
htk_ammo        = "r"
htk_haste       = "4"

#in case ping latency is too high, increase the waiting time
#Use only integer values
global walk_lag_delay 
walk_lag_delay = 2

#starting waypoint configuration
wp = 1
label = "hunt"

#calls script selector
script_selector_function()
App.focus("Tibia")

#shows ping on game screen
type(Key.F8, KeyModifier.ALT)

#mute system
subprocess.Popen(['osascript', '-e', 'set Volume 0'])

#adjusts the minimap zoom
minimap_adjustment()

##################################################################
 ######     ###    ##     ## ######## ########   #######  ######## 
##    ##   ## ##   ##     ## ##       ##     ## ##     ##    ##    
##        ##   ##  ##     ## ##       ##     ## ##     ##    ##    
##       ##     ## ##     ## ######   ########  ##     ##    ##    
##       #########  ##   ##  ##       ##     ## ##     ##    ##    
##    ## ##     ##   ## ##   ##       ##     ## ##     ##    ##    
 ######  ##     ##    ###    ######## ########   #######     ##    
##################################################################

#Main
while True:

    #makes console frame appear (BUG: it may vanish after a while)
    frame.visible = True
    
    #hover(Location(screen_center_x,screen_center_y))
    if label == "hunt": attack_function()
    #statusBar_check()
    
    try: 
        wp_action = waypointer(label,wp)
        #verifies if should perform some action when reaches destination
        if wp_action > 0:
            waypoint_action(wp_action)
        print "Arrived at",label,"waypoint",wp
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Arrived at "+label+" waypoint "+str(wp))
        
        #########################################
        #current waypoint is the last one for hunt
        if (label == "hunt" and wp >= last_hunt_wp):
            
            #check if it should leave the hunt
            print "Checking for exit conditions..."
            messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Checking for exit conditions...")
            label = imported_script.check_exit()
            wp = 1
            messageTOP.setText("Current Waypoint: "+label+" "+str(wp))
            
        ##########################################
        #current waypoint is the last one for leave
        elif label == "leave" and wp >= last_leave_wp:
            
            #check if there is battle-on icon
            statusBar = Region(1111,335,110,14)
            if statusBar.exists("battleon.png"):
                waitVanish("battleon.png",30)
                logoff_function()
            else: logoff_function()
        
        ##########################################
        #no criterea matched
        else: 
            wp+=1
            messageTOP.setText("Current Waypoint: "+label+" "+str(wp))
    
    except:
        print "[ATTENTION] Waypoint",wp,"not found for",label
        messageCENTER.setText(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"[ATTENTION] Waypoint "+str(wp)+" not found for "+label)
        wp+=1
        messageTOP.setText("Current Waypoint: "+label+" "+str(wp))
        pass

#end
