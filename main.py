#TMB - Tibia Mac Bot

#library imports
import os
import subprocess
import re
import math
import importlib
import json
from datetime import *
from javax.swing import JFrame, JButton, JLabel, JScrollPane, JTextArea, JPanel
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

    statusBar = Region(1111,335,110,14)
    
    if statusBar.exists("battleon.png"):
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Battle icon on - Waiting 30 secs"+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())
        wait(30)
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Trying to logoff again..."+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())
        logoff_function()
        
    else:
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Printing Screen"+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())
        type("3", KeyModifier.CMD + KeyModifier.SHIFT)
        type("l", KeyModifier.CMD)
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"[END OF EXECUTION]"+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())
    
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

    #textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Pixel Analyzed: "+color+"\n")
    #textArea.setCaretPosition(textArea.getDocument().getLength())
    
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

    textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Walking to "+label+" waypoint "+str(wp)+"\n")
    textArea.setCaretPosition(textArea.getDocument().getLength())
    
    if label == "go_hunt":
        wp_action = imported_script.label_go_hunt(wp)
    
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

                returned_color = get_pixel_color(960,77)
                if returned_color != "3f3f3f": #means there is a mob on battle list
                    textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Mob detected while walking"+"\n")
                    textArea.setCaretPosition(textArea.getDocument().getLength())

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
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Action 1 - Using rope"+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())

        
    if wp_action == 2:
        click(Location(screen_center_x,screen_center_y))
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Action 2 - Using ladder"+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())

        
    if wp_action == 3:
        type(htk_shovel)
        click(Location(screen_center_x,screen_center_y))
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Action 3 - Using shovel"+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())

        
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
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Battle list is clear"+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())
        return
    
    else:
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Monster detected on screen"+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())
        type(Key.SPACE)        
        attacking(0,1)
        #wait untill mob is dead to get loot
        if take_loot == 1: melee_looter()
        #call function again to check if there is another mob on the battle list
        attack_function()


#function to verify if its currently attacking a mob
def attacking(slot,atkCount):

    #textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Attacking slot "+str(slot)+" - "+str(atkCount)+"/30 \n")
    #textArea.setCaretPosition(textArea.getDocument().getLength())

    #verifies health and mana
    healer_function()

    if atkCount >= 30:
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Trap or unreachable - Switching Target \n")
        textArea.setCaretPosition(textArea.getDocument().getLength())
        type(Key.SPACE)
        slot+=1
        atkCount=0

    #distance between slots is 22 pixels
    returned_color = get_pixel_color(932,60+(slot*22))
      
    if (returned_color == 'ff0000' or returned_color == 'ff7f7d'): #red or whitish-red
        attacking(slot,atkCount+1)

    if returned_color == 'ffffff':
        type(Key.SPACE)
        attacking(0,1)

    else: return

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
    textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Looting around char"+"\n")
    textArea.setCaretPosition(textArea.getDocument().getLength())

    #1 2 3
    #8 9 4
    #7 6 5
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

    #Life < 50%
    returned_color = get_pixel_color(1172,166)
    if returned_color != "922d2b": type(htk_life_pot)

    #Life < 85%
    returned_color = get_pixel_color(1192,166)
    if returned_color != "922d2b": type(htk_life_spell)
    
    #Mana < 50%
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
    
    if ring_slot.exists(Pattern("empty_ring.png").exact()):type(htk_ring)
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
            "[RK] Rook Troll PA",
            "[EK] Amazon Camp"
    )
    prompt = select("Please select a script from the list","Available Scripts", options = script_list, default = script_list[0])

    if prompt == script_list[0]:
        popup("You did not choose a script - Terminating!")
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"[WARNING] No Script Selected \n [END OF EXECUTION]")
        textArea.setCaretPosition(textArea.getDocument().getLength())
        type('c', KeyModifier.CMD + KeyModifier.SHIFT)
        
    if prompt == script_list[1]:
        selected_script = "rook_psc"
        script_loader(selected_script)

    if prompt == script_list[2]:
        selected_script = "mino_hell"
        script_loader(selected_script)

    if prompt == script_list[3]:
        selected_script = "rook_troll"
        script_loader(selected_script)


    if prompt == script_list[4]:
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
    global last_go_hunt_wp
    
    textArea.append("[CORE] Selected Script: "+selected_script+"\n")
    textArea.setCaretPosition(textArea.getDocument().getLength())

    #imports the script that will be executed on this session
    imported_script = importlib.import_module(selected_script)
           
    #reads the value from the import script
    combat_mode     = imported_script.combat_mode
    take_loot       = imported_script.take_loot
    lure_mode       = imported_script.lure_mode
    equip_ring      = imported_script.equip_ring
    refill_ammo     = imported_script.refill_ammo
    minimap_zoom    = imported_script.minimap_zoom
    last_hunt_wp    = imported_script.last_hunt_wp
    last_leave_wp   = imported_script.last_leave_wp
    last_go_hunt_wp = imported_script.last_go_hunt_wp

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
    textArea.append("[CORE] Adjusting minimap zoom to "+str(minimap_zoom)+"\n")
    textArea.setCaretPosition(textArea.getDocument().getLength())
    click(Location(1240,128))
    click(Location(1240,128))
    click(Location(1240,128))

    if minimap_zoom == 1:
        click(Location(1240,110))
    if minimap_zoom == 2:
        click(Location(1240,110))
        click(Location(1240,110))


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
             
###############################################
######## ########     ###    ##     ## ######## 
##       ##     ##   ## ##   ###   ### ##       
##       ##     ##  ##   ##  #### #### ##       
######   ########  ##     ## ## ### ## ######   
##       ##   ##   ######### ##     ## ##       
##       ##    ##  ##     ## ##     ## ##       
##       ##     ## ##     ## ##     ## ######## 
###############################################

frame = JFrame("Console Log")
frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
frame.setBounds(360,630,550,140);
contentPane = JPanel()
frame.setContentPane(contentPane)
textArea = JTextArea(6,44)
textArea.setEditable(False)
contentPane.add(textArea)
scrollPane = JScrollPane(textArea, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
contentPane.add(scrollPane)
frame.setAlwaysOnTop(True)
frame.setVisible(True)

textArea.append("[STARTING EXECUTION]"+"\n")
textArea.setCaretPosition(textArea.getDocument().getLength())

###############################################
#calls script selector
script_selector_function()

#in case ping latency is too high, increase the waiting time
#Use only integer values
global walk_lag_delay 
walk_lag_delay = 1

#starting waypoint configuration
wp = 1
#label = "go_hunt"
label = select("Please select a starting point","Available Starting Points", options = ("go_hunt","hunt","leave"), default = "go_hunt")
textArea.append("[CORE] Starting at "+label+", waypoint "+str(wp)+"\n")
textArea.setCaretPosition(textArea.getDocument().getLength())

#set focus on game client
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
            
        #After arriving at destination waypoint
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"Arrived at "+label+" waypoint "+str(wp)+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())
        
        #########################################
        #current waypoint is the last one for hunt
        if (label == "hunt" and wp >= last_hunt_wp):
            
            #check if it should leave the hunt
            textArea.append("[CORE] Checking for exit conditions...\n")
            textArea.setCaretPosition(textArea.getDocument().getLength())
            label = imported_script.check_exit()
            wp = 1
            
        ##########################################
        #current waypoint is the last one for leave
        elif label == "leave" and wp >= last_leave_wp:
            logoff_function()
            
        ##########################################
        #current waypoint is the last one for go_hunt
        elif label == "go_hunt" and wp >= last_go_hunt_wp:
            textArea.append("[CORE] Setting label to Hunt\n")
            textArea.setCaretPosition(textArea.getDocument().getLength())
            label = "hunt"
            wp = 1
            
        ##########################################
        #no criterea matched
        else: 
            wp+=1
    except:
        textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+"[ERROR] Waypoint "+str(wp)+" not found for "+label+"\n")
        textArea.setCaretPosition(textArea.getDocument().getLength())
        wp+=1
        pass

#end
