#desenvolvido por gmargonato
#inicio da construcao: 08/junho/2020

import os
import subprocess
import re
import importlib
import json
import datetime

Settings.ObserveScanRate = 10
Settings.MoveMouseDelay = 0
Settings.ActionLogs = 0

#configuracoes de hotkeys
lifePotion = Key.F1
healSpell = Key.F2
manaPotion = Key.F3
keyAtkSpell = Key.F5
keyPoison = Key.F10
keyFood = Key.F12
keyRope = "o"
keyShovel = "p"
keyRing = "l"

#inicio
wp = 1
use_spell = 0
seletor_scripts()
App.focus("Tibia")

#loop principal de execucao
while True:

    atacar()
    statusBar_check()
    
    if equip_ring == 1: check_ring()

    try:andar(wp)
    except:
        print "[ERRO] Waypoint", wp,"nao encontrado!"    
        pass

    dropa o item no ultimo Wp
    if wp == wp_final and drop == 1: modulo.dropar()
    
    wp+=1
    if wp > wp_final: wp = 1
