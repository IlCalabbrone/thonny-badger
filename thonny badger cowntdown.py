import badger2040
import badger_os
from pimoroni_i2c import PimoroniI2C
from breakout_rtc import BreakoutRTC
import time

badger = badger2040.Badger2040()
badger.set_update_speed(badger2040.UPDATE_FAST)

# RTC
i2c = PimoroniI2C(sda=4, scl=5)
rtc = BreakoutRTC(i2c)
rtc.clear_alarm_flag()

# configurato=0 primo avvio
state = {"configurato": 0, "giorni": 0, "ore": 0}
badger_os.state_load("countdown", state)


# MENU

def disegna_menu(valori, campo_sel):
    campi = ["Anni  ", "Giorni", "Ore   "]
    badger.set_pen(15)
    badger.clear()
    badger.set_pen(0)

    # titolo
    badger.text("IMPOSTA COUNTDOWN", 10, 4, 2)

    # campi
    for i in range(3):
        y = 38 + i * 26
        if i == campo_sel:
            # Campo selezionato: sfondo nero, testo bianco
            badger.set_pen(0)
            badger.rectangle(4, y - 4, 288, 22)
            badger.set_pen(15)
        else:
            badger.set_pen(0)
        badger.text(f"{campi[i]}: {valori[i]:>4}", 14, y, 2)

    # pulsanti-
    badger.set_pen(0)
    badger.text("SU/GIU valore   A << campo >> C   B conferma", 4, 116)

    badger.update()


# LOOP giorni_tot, ore

def setup_menu():
    valori = [0, 0, 0]   # anni, giorni, ore
    campo_sel = 0

    disegna_menu(valori, campo_sel)

    while True:
        time.sleep(0.15)  

        cambiato = False

        if badger.is_pressed(badger2040.BUTTON_UP):
            valori[campo_sel] += 1
            cambiato = True

        elif badger.is_pressed(badger2040.BUTTON_DOWN):
            if valori[campo_sel] > 0:
                valori[campo_sel] -= 1
            cambiato = True

        elif badger.is_pressed(badger2040.BUTTON_A):   # prec
            if campo_sel > 0:
                campo_sel -= 1
            cambiato = True

        elif badger.is_pressed(badger2040.BUTTON_C):   # succ
            if campo_sel < 2:
                campo_sel += 1
            cambiato = True

        elif badger.is_pressed(badger2040.BUTTON_B):   # conf
            giorni_tot = valori[0] * 365 + valori[1]
            return giorni_tot, valori[2]

        if cambiato:
            disegna_menu(valori, campo_sel)


# PRIMO AVVIO → mostra il menu di setup
# tieni premuto A all'avvio reset

if not state["configurato"] or badger.is_pressed(badger2040.BUTTON_A):
    giorni, ore = setup_menu()
    state["configurato"] = 1
    state["giorni"] = giorni
    state["ore"] = ore
    badger_os.state_save("countdown", state)


# DISEGNA IL COUNTDOWN NORMALE

badger.set_update_speed(badger2040.UPDATE_NORMAL)
badger.set_pen(15)
badger.clear()
badger.set_pen(0)

if state["giorni"] == 0 and state["ore"] == 0:
    badger.text("Countdown", 10, 50, 2)
    badger.text("finito!", 10, 90, 2)
else:
    badger.text("Mancano esattamente", 10, 10)
    badger.text("Giorni: " + str(state["giorni"]), 10, 40, 2)
    badger.text("Ore:    " + str(state["ore"]), 10, 75, 2)

    if state["ore"] == 0:
        state["giorni"] -= 1
        state["ore"] = 23
    else:
        state["ore"] -= 1

    badger_os.state_save("countdown", state)

badger.update()


# DEEP SLEEP 

rtc.set_alarm(0, minutes=0)
rtc.enable_alarm_interrupt(True)
badger.halt()