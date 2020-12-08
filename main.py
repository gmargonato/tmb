#AppleBot

#library imports
import os
import subprocess
import re
import math
import importlib
import json
import threading
import shutil
from datetime import *
from random import *
from javax.swing import JFrame, JButton, JLabel, JScrollPane, JTextArea, JPanel, JButton
from java.awt.BorderLayout import *
from java.awt import Robot, Color
from sikuli import *

#basic sikuli configurations
Settings.ObserveScanRate = 10
Settings.MoveMouseDelay = 0
Settings.ActionLogs = 0

############################################################
 ######   #######  ##    ## ######## ####  ######    ######  
##    ## ##     ## ###   ## ##        ##  ##    ##  ##    ## 
##       ##     ## ####  ## ##        ##  ##        ##       
##       ##     ## ## ## ## ######    ##  ##   ####  ######  
##       ##     ## ##  #### ##        ##  ##    ##        ## 
##    ## ##     ## ##   ### ##        ##  ##    ##  ##    ## 
 ######   #######  ##    ## ##       ####  ######    ######  
############################################################

#in case ping latency is too high, increase the waiting time (use only integer values)
global walk_interval
walk_interval = 2

#center of screen (char's feet coordinates)
global screen_center_x
global screen_center_y
screen_center_x = 463
screen_center_y = 297

#tools
rope   = "o"  
shovel = "p"
ring   = "l"
amulet = "k"
food   = "u"

#spells
exana_pox = "i"
haste = "v"
utura = "5"
exeta_res = ["exeta res","6","atk",6]

#############################################################
########  ########  ######   ####  #######  ##    ##  ######  
##     ## ##       ##    ##   ##  ##     ## ###   ## ##    ## 
##     ## ##       ##         ##  ##     ## ####  ## ##       
########  ######   ##   ####  ##  ##     ## ## ## ##  ######  
##   ##   ##       ##    ##   ##  ##     ## ##  ####       ## 
##    ##  ##       ##    ##   ##  ##     ## ##   ### ##    ## 
##     ## ########  ######   ####  #######  ##    ##  ######  
#############################################################

#watchable regions
debuff_region     = Region(1111,451,110,15)
equip_region      = Region(1109,307,114,145)
battlelist_region = Region(1104,469,30,120)
game_region       = Region(226,124,474,348)
message_region   = Region(226,443,477,31)
action_bar_region = Region(1,482,925,40)

#############################################################################################
########  #### ##     ## ######## ##           ######   #######  ##        #######  ########  
##     ##  ##   ##   ##  ##       ##          ##    ## ##     ## ##       ##     ## ##     ## 
##     ##  ##    ## ##   ##       ##          ##       ##     ## ##       ##     ## ##     ## 
########   ##     ###    ######   ##          ##       ##     ## ##       ##     ## ########  
##         ##    ## ##   ##       ##          ##       ##     ## ##       ##     ## ##   ##   
##         ##   ##   ##  ##       ##          ##    ## ##     ## ##       ##     ## ##    ##  
##        #### ##     ## ######## ########     ######   #######  ########  #######  ##     ##
#############################################################################################

#returns the color (HEX) of one exact pixel on the screen
def pixelColor(posX,posY):   
    pixel = Robot().getPixelColor(posX,posY)
    r = pixel.getRed()
    g = pixel.getGreen() 
    b = pixel.getBlue() 
    color = '{:02x}{:02x}{:02x}'.format(r,g,b)
    return color

#to be used exclusively by the healer thread
def healerColor(posX,posY):
    pixel = Robot().getPixelColor(posX,posY)
    r = pixel.getRed()
    g = pixel.getGreen() 
    b = pixel.getBlue() 
    color = '{:02x}{:02x}{:02x}'.format(r,g,b)
    #print "Color at",posX,posY,":",color
    return color

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
    
    if debuff_region.exists("battleon.png"):
        log("Battle icon on - Waiting 30 secs")
        attack_function()
        wait(30)
        log("Trying to logoff again...")
        logoff_function()
        
    else:
        log("Printing Screen")
        type("3", KeyModifier.CMD + KeyModifier.SHIFT)
        type("l", KeyModifier.CMD)
        log("[END OF EXECUTION]")
        closeFrame(0)

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
    log("Walking to "+label+" waypoint "+str(wp)) 
    if label == "go_hunt":
        wp_action = imported_script.label_go_hunt(wp)
    
    if label == "hunt":
        wp_action = imported_script.label_hunt(wp)
        
    if label == "leave":
        wp_action = imported_script.label_leave(wp)

    #moves mouse back to center of screen 
    hover(Location(screen_center_x,screen_center_y))

    #checks if the Char has stopped or continues walking
    walking_check(0,wp_action,label,wp)
    
    return wp_action
 
def walking_check(time_stopped,wp_action,label,wp):
    while time_stopped != walk_interval:
        minimap_region    = Region(1109,161,115,119)
        minimap_region.onChange(1,changeHandler)
        minimap_region.somethingChanged = False
        minimap_region.observe(1)
        
        #if enters here, means char is still walking
        if minimap_region.somethingChanged:
            time_stopped = 0
            while debuff_region.exists("paralysed.png",0): 
                type(haste)
                wait(0.5)
            
            #verifies if it should engage combat while walking
            if label == "hunt" and lure_mode == 0: 
                slot1 = pixelColor(1130,500)
                if slot1 == "000000":
                    log("Mob detected on battle list while walking")
                    type(Key.ESC)
                    wait(0.5)
                    attack_function()
                    if running == 1: waypointer(label,wp)
                else: pass
                
            #in case shouldn't engane combat
            else: pass
        
        #if nothing changes on the screen for some time, add 1 to stopped timer
        if not minimap_region.somethingChanged:
            time_stopped+=1

        continue
    else: return

#function to verify if something is changing on screen
def changeHandler(event):
    event.region.somethingChanged = True
    event.region.stopObserver()

#wp_action list:
        #1: use rope
        #2: use ladder
        #3: use shovel

def waypoint_action(wp_action): 
    if wp_action == 1:
        type(rope)
        click(Location(screen_center_x,screen_center_y))
        log("Using rope")
        
    if wp_action == 2:
        click(Location(screen_center_x,screen_center_y))
        log("Using ladder")
        
    if wp_action == 3:
        type(shovel)
        click(Location(screen_center_x,screen_center_y))
        log("Using shovel")    
        
    wait(1)
    return

########################################################
########    ###    ########   ######   ######## ######## 
   ##      ## ##   ##     ## ##    ##  ##          ##    
   ##     ##   ##  ##     ## ##        ##          ##    
   ##    ##     ## ########  ##   #### ######      ##    
   ##    ######### ##   ##   ##    ##  ##          ##    
   ##    ##     ## ##    ##  ##    ##  ##          ##    
   ##    ##     ## ##     ##  ######   ########    ##   
########################################################

def attack_function():

    type(Key.SPACE)
    wait(0.3)

    attacking()
    
    #img = capture(game_region)
    #shutil.move(img,os.path.join(r"/Users/GabrielMargonato/Downloads/SIKULI/DATASET/"+str(int(time.time()))+'.png'))
    
    #checks for new mob on screen
    slot1 = pixelColor(1130,500)
    if slot1 == "000000": attack_function()
    
    else:
        log("Battle list clear")
        return
    
def attacking(): 
   
    battlelist_region.waitVanish("bl_target.png",30) #waits for 30 seconds before switching mob
    
    #after mob is dead:
    
    if loot_type == 1: 
        melee_looter()
        if message_region.exists("valuable_loot.png",0): 
            log("[LOOTER] Valuable loot dropped!")
            melee_looter()
        
    elif loot_type == 2 and message_region.exists("valuable_loot.png",0):
        log("[LOOTER] Valuable loot dropped!")
        melee_looter()
        melee_looter()

    elif loot_type == 3: 
        try:target_loot()
        except: pass

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

#loot_type = 0 -> dont take loot at all
#loot_type = 1 -> loot everything
#loot_type = 2 -> loot only valuable
#loot_type = 3 -> automaticly identy and loot corpse on the game_region

def melee_looter():
    log("Looting around char")
    click(Location(430,265),8) #1
    click(Location(462,265),8) #2
    click(Location(495,265),8) #3
    click(Location(495,297),8) #4   
    click(Location(495,330),8) #5
    click(Location(462,330),8) #6
    click(Location(430,330),8) #7    
    click(Location(430,297),8) #8
    click(Location(screen_center_x,screen_center_y),8) #9

def target_loot():
    wait(1)
    corpses_on_screen = findAnyList(loot_corpses)
    for corpse in corpses_on_screen:
        log("Looting at "+str(corpse.getX())+","+str(corpse.getY()))
        click(corpse,8)
        hover(Location(screen_center_x,screen_center_y))
        last_loot_region = Region(3,760,173,18)
        last_loot_region.wait("looted_1.png",3)
        break
 
###########
# THREADS #  
###########

#function to prevent being exhausted
def sendHotkey(actionList):
    
    #                0        1       2       3
    #actionList = ["name","hotkey","type",cooldown]
    
    global lastHeal
    global lastObj
    global lastSupp
    
    #                0        1       2       3        4
    #actionList = ["name","hotkey","type",cooldown,last_cast]

    global atk_spell_1
    global atk_spell_2
    global atk_spell_3
    
    now = datetime.now()
               
    if actionList[2] == "heal":
    
        diff = (now - lastHeal).total_seconds()
        if diff >= actionList[3]:
            log("Casting heal spell \'"+actionList[0]+"\'")
            type(actionList[1])        
            lastHeal = datetime.now()

    if actionList[2] == "object":
    
        diff = (now - lastObj).total_seconds()
        if diff >= actionList[3]:
            log("Using item \'"+actionList[0]+"\'")
            type(actionList[1])        
            lastObj = datetime.now()
     
    if actionList[2] == "atk":
        
        diff = (now - actionList[4]).total_seconds()
        if diff >= actionList[3]:
            log("Casting attack spell \'"+actionList[0]+"\'")            
            type(actionList[1])        
            actionList[4] = datetime.now()
            sleep(2)


#Healing
def healer_function(arg):
    while running == 1:

        if running == 0: break

        if vocation == 0:

            life = healerColor(15,55)
            if life == "bc8900" or life == "b01a20": 
                sendHotkey(light_heal) 
                if life == "b01a20":
                    img = capture(Screen().getBounds())
                    shutil.move(img,os.path.join(r"/Users/GabrielMargonato/Downloads/SIKULI/SESSIONS/"+str(session_id)+'_red_life.png'))
       
            sleep(1)
            continue
            
        else:

            life = healerColor(15,55)
            if life == "b01a20": 
                sendHotkey(emergency_heal)  
                img = capture(Screen().getBounds())
                shutil.move(img,os.path.join(r"/Users/GabrielMargonato/Downloads/SIKULI/SESSIONS/"+str(session_id)+'_red_life.png'))
       
            mana = healerColor(660,71)
            if mana != "00266d": sendHotkey(mana_pot)  
            
            if life == "bc8900": sendHotkey(intense_heal)         
            if life == "5a9200": sendHotkey(light_heal)  

    else: print "Ending healer thread"

def startHealerThread():
    healer_thread = threading.Thread(target=healer_function, args = (0,))
    if healer_thread.isAlive() == False:
        print "Starting healer thread"
        healer_thread.start()
    else: 
        print "[ERROR] Healer thread already running"
    
#Targeting Spell  
def spell_caster_function(arg):
    while running == 1:  
        
        if battlelist_region.exists("bl_target.png",0):   
            
            #cast primary atk spell
            sendHotkey(atk_spell_1)
            if lure_mode == 1 or use_exeta == 1: sendHotkey(exeta_res)

            if lure_mode == 1:     near_targets("box")
            if stay_diagonal == 1: near_targets("diagonal")
            if take_distance == 1: near_targets("distance")

            if running == 0: break

        else: sleep(1)
    
    else: print "Ending spell caster thread"

def startSpellCasterThread():
    spell_cast_thread = threading.Thread(target=spell_caster_function, args = (0,))
    if spell_cast_thread.isAlive() == False:
        print "Starting spell caster thread"
        spell_cast_thread.start()
    else: 
        print "[ERROR] Spell caster thread already running"
    
    
#checks for targets around character
def near_targets(mode):

    #1 2 3
    #4 c 5
    #6 7 8

    pos1 = pixelColor(445,247)
    pos2 = pixelColor(477,247)
    pos3 = pixelColor(509,247)
    pos4 = pixelColor(445,279)    
    pos5 = pixelColor(509,279)
    pos6 = pixelColor(445,311)
    pos7 = pixelColor(477,311)
    pos8 = pixelColor(509,311)

    ######################
    if mode == "box":
        
        targets_around = 0
      
        if pos1 == "000000": targets_around += 1   
        if pos2 == "000000": targets_around += 1
        if pos3 == "000000": targets_around += 1
        if pos4 == "000000": targets_around += 1
        if pos5 == "000000": targets_around += 1                
        if pos6 == "000000": targets_around += 1        
        if pos7 == "000000": targets_around += 1       
        if pos8 == "000000": targets_around += 1
        
        if targets_around >= 4: 
            sendHotkey(atk_spell_2)
            return

        else:

            if (pos1 == "000000" and pos2 == "000000" and pos3 == "000000"):
                type(Key.UP, KeyModifier.CMD)
                sendHotkey(atk_spell_3)
                return
            
            elif (pos1 == "000000" and pos4 == "000000" and pos6 == "000000"): 
                type(Key.LEFT, KeyModifier.CMD)
                sendHotkey(atk_spell_3)
                return
            
            elif (pos6 == "000000" and pos7 == "000000" and pos8 == "000000"):
                type(Key.DOWN, KeyModifier.CMD)
                sendHotkey(atk_spell_3)
                return
            
            elif (pos3 == "000000" and pos5 == "000000" and pos8 == "000000"):
                type(Key.RIGHT, KeyModifier.CMD)
                sendHotkey(atk_spell_3)
                return

    ######################
    if mode == "diagonal":
        
        if (pos2 == "000000" or pos7 == "000000"): 
            walk = randint(1,2)
            if walk == 1: type(Key.LEFT)
            if walk == 2: type(Key.RIGHT)
            return
        elif (pos4 == "000000" or pos5 == "000000"): 
            walk = randint(1,2)
            if walk == 1: type(Key.UP)
            if walk == 2: type(Key.DOWN)
            return
        else: return
    
    if mode == "distance":

        targetLifeBar = "target_life_bar.png"

        gr1 = Region(225,125,255,185)
        gr2 = Region(449,124,252,191)
        gr3 = Region(226,284,253,187)
        gr4 = Region(450,284,251,187)
        if gr1.exists(targetLifeBar,0): 
            type(Key.RIGHT);type(Key.DOWN)
            
        if gr2.exists(targetLifeBar,0): 
            type(Key.LEFT);type(Key.DOWN)
            
        if gr3.exists(targetLifeBar,0): 
            type(Key.RIGHT);type(Key.UP)
            
        if gr4.exists(targetLifeBar,0): 
            type(Key.LEFT);type(Key.UP)
            
        sleep(1)

####################################################################
########  ########   #######  ########  ########  ######## ########  
##     ## ##     ## ##     ## ##     ## ##     ## ##       ##     ## 
##     ## ##     ## ##     ## ##     ## ##     ## ##       ##     ## 
##     ## ########  ##     ## ########  ########  ######   ########  
##     ## ##   ##   ##     ## ##        ##        ##       ##   ##   
##     ## ##    ##  ##     ## ##        ##        ##       ##    ##  
########  ##     ##  #######  ##        ##        ######## ##     ## 
####################################################################

def drop_item(sprite,name):
    if exists(sprite,0):
        imageCount = len(list([x for x in findAll(sprite)]))
        for i in range(imageCount):
            log("Dropping "+name+" "+str(i+1)+"/"+str(imageCount))
            dragDrop(sprite, Location(screen_center_x,screen_center_y))
            wait(0.5)
    else: return
    
########################################################################################
# DEBUFF
########################################################################################

def debuff_check():
    if action_bar_region.exists(Pattern("1607028632854.png").exact(),0) or action_bar_region.exists(Pattern("1607028692864.png").exact(),0): type(utura)
    #while debuff_region.exists("paralysed.png",0): type(haste)
    #while debuff_region.exists("food.png",0): type(food)
    #while debuff_region.exists("poison.png",0): type(exana_pox)
    if (equip_ring == 1 and equip_region.exists("ring.png",0)): type(ring)
    if (equip_amulet == 1 and equip_region.exists("amulet.png",0)): type (amulet)
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
            "Rook Mino Hell",
            "Yalahar Mutated Tigers",
            "Edron Bog Raider"
    )
    prompt = select("Please select a script from the list","Available Scripts", options = script_list, default = script_list[0])

    global selected_script

    if   prompt == script_list[1]: selected_script = "mino_hell" 
    elif prompt == script_list[2]: selected_script = "ylr_mut_tiger"
    elif prompt == script_list[3]: selected_script = "bog_raider_edron" 
    else:
        popup("The selected script is not valid, terminating execution")
        closeFrame(0)
        raise Exception("Invalid Script")
       
    log("Selected Script: "+selected_script)

    #declare global variables
    global imported_script
    
    global vocation      
    global loot_type     
    global lure_mode  
    global use_exeta
    global equip_ring    
    global equip_amulet  
    global drop_vials    
    global stay_diagonal 
    global take_distance 
    
    global utura
    global light_heal    
    global intense_heal  
    global emergency_heal
    global mana_pot   
    
    global atk_spell_1
    global atk_spell_2
    global atk_spell_3
    
    global minimap_zoom
    global last_hunt_wp
    global last_leave_wp
    global last_go_hunt_wp
    
    #imports the script that will be executed on this session
    imported_script = importlib.import_module(selected_script)
    
    #set variables
    vocation      = imported_script.vocation
    loot_type     = imported_script.loot_type

    if loot_type == 3: 
        global loot_corpses
        loot_corpses = imported_script.loot_corpses
                                                            
    lure_mode     = imported_script.lure_mode

    try: use_exeta = imported_script.use_exeta
    except: use_exeta = 0
    
    equip_ring    = imported_script.equip_ring
    equip_amulet  = imported_script.equip_amulet
    drop_vials    = imported_script.drop_vials
    stay_diagonal = imported_script.stay_diagonal
    take_distance = imported_script.take_distance

    #heal
    light_heal     = imported_script.light_heal
    intense_heal   = imported_script.intense_heal
    emergency_heal = imported_script.emergency_heal
    mana_pot       = imported_script.mana_pot
    
    #atk
    atk_spell_1 = imported_script.atk_spell_1  
    atk_spell_2 = imported_script.atk_spell_2
    atk_spell_3 = imported_script.atk_spell_3

    minimap_zoom    = imported_script.minimap_zoom
    last_hunt_wp    = imported_script.last_hunt_wp
    last_leave_wp   = imported_script.last_leave_wp
    last_go_hunt_wp = imported_script.last_go_hunt_wp
    
###############################################
######## ########     ###    ##     ## ######## 
##       ##     ##   ## ##   ###   ### ##       
##       ##     ##  ##   ##  #### #### ##       
######   ########  ##     ## ## ### ## ######   
##       ##   ##   ######### ##     ## ##       
##       ##    ##  ##     ## ##     ## ##       
##       ##     ## ##     ## ##     ## ######## 
###############################################

#receives a message and print it onto jframe
def log(message):
    textArea.append(str(datetime.now().strftime("%H:%M:%S.%f - "))+str(message)+"\n")
    textArea.setCaretPosition(textArea.getDocument().getLength())

def closeFrame(event):
    global running
    running = 0
    frame.dispose()

frame = JFrame("AppleBot - Console Log")
frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
frame.setBounds(8,545,600,70)
contentPane = JPanel()
frame.setContentPane(contentPane)

buttonS = JButton("STOP", actionPerformed = closeFrame)
buttonS.setForeground(Color.RED)
frame.add(buttonS,WEST)

textArea = JTextArea(6,38)
#textArea.setFont(textArea.getFont().deriveFont(textArea.getFont().getSize() - 2.5))
textArea.setEditable(False)
contentPane.add(textArea)
scrollPane = JScrollPane(textArea, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
contentPane.add(scrollPane)
frame.setUndecorated(True)
frame.setAlwaysOnTop(True)
frame.pack()
frame.setVisible(True)
log("Initializing bot")

###############################################
############### BOT STARTS HERE ###############
###############################################

#generates an ID for this session
session_id = str(datetime.now().strftime("%d%m%Y%H%M"))
log("Session ID: "+str(session_id))

#calls script selector
script_selector_function()

#starting label
label = select("Please select a starting point","Available Starting Points", options = ("go_hunt","hunt","leave"), default = "go_hunt")

#starting waypoint number
if label == "go_hunt":
    available_wps = list(range(1,last_go_hunt_wp+1))
    
if label == "hunt":
    available_wps = list(range(1,last_hunt_wp+1))

if label == "leave":
    available_wps = list(range(1,last_leave_wp+1))

list_of_wps = map(str, available_wps)
wp_str = select("Choose a starting waypoint",label, list_of_wps, default = 0)
wp = int(wp_str)

log("Starting at "+label+" waypoint "+str(wp))
log("[ATTENTION] Walk interval is set to "+str(walk_interval)+" seconds")


#If game client exists, focus on it. Else, throws exception
if(App("Tibia").isRunning() == True): App.focus("Tibia")
else:
    frame.dispose()
    raise Exception('Tibia client not running.')

#shows ping on game screen
if not exists(Pattern("ping.png").similar(0.50),0): type(Key.F8, KeyModifier.ALT)

#adjusts the starting minimap zoom for this session
def adjust_minimap_zoom():
    #subtract zoom
    for i in range(0,3):
        click(Location(1240,246))
    
        #add zoom
    for i in range(0,minimap_zoom):
        click(Location(1240,227))

log("Adjusting minimap zoom to "+str(minimap_zoom))
adjust_minimap_zoom()

#sets session channel
if loot_type >= 1: click("loot_channel.png")
else: click("server_log_channel.png")

#start threads
lastObj  = datetime.now()
lastHeal = datetime.now()
lastSupp = datetime.now()    
atk_spell_1.append(datetime.now())
atk_spell_2.append(datetime.now())
atk_spell_3.append(datetime.now())
exeta_res.append(datetime.now())


running = 1
startHealerThread()
if vocation > 0: startSpellCasterThread()


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
while running == 1:
 
    if label == "hunt": 
        slot1 = pixelColor(1130,500)
        if slot1 == "000000": 
            log("Mob detected on battle list")
            attack_function()
        if vocation > 0: debuff_check()

    if running == 0: closeFrame(0);break
    
    try: 
        wp_action = waypointer(label,wp)
        #verifies if should perform some action when reaches destination
        if wp_action > 0: waypoint_action(wp_action)
            
        #After arriving at destination waypoint
        log("Arrived at "+label+" waypoint "+str(wp))
        
        #########################################
        #current waypoint is the last one for hunt
        if (label == "hunt" and wp >= last_hunt_wp):

            #check if should drop vials
            if drop_vials == 1: 
                log("Looking for vials to drop...")
                drop_item(Pattern("small_flask.png").exact(),"small empty flask")
                drop_item(Pattern("strong_flask.png").exact(),"strong empty flask")
                drop_item(Pattern("great_flask.png").exact(),"great empty flask")
            
            #check if it should leave the hunt
            log("Checking for exit conditions...")
            label = imported_script.exit_conditions()

            #reset waypoint back to 1
            wp = 1
               
            #prints the screen after a sucessfull run and saves it
            log("Printing session ID "+str(session_id)) 
            img = capture(Screen().getBounds())
            shutil.move(img,os.path.join(r"/Users/GabrielMargonato/Downloads/SIKULI/SESSIONS/"+session_id+'.png'))
    
        ##########################################
        #current waypoint is the last one for leave
        elif label == "leave" and wp >= last_leave_wp:
            logoff_function()
            
        ##########################################
        #current waypoint is the last one for go_hunt
        elif label == "go_hunt" and wp >= last_go_hunt_wp:
            log("Setting label to Hunt")
            label = "hunt"
            wp = 1
            
        ##########################################
        #no criterea matched
        else: 
            wp+=1
    except:
        log("[ERROR] waypoint "+label+" "+str(wp)+" not found!")
        #move to next waypoint
        if   label == "go_hunt" and wp > last_go_hunt_wp:
            adjust_minimap_zoom()
            wp = 1
        elif label == "hunt"    and wp > last_hunt_wp: 
            adjust_minimap_zoom()
            wp = 1
        elif label == "leave"   and wp > last_leave_wp: 
            adjust_minimap_zoom()
            wp = 1
        else: wp+=1

else: popup("END")
#end
