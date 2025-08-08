import time, threading
import numpy as np
import sounddevice as sd
import pyautogui
from config import THRESHOLD, CLAP_TIMEOUT, ACTION_DELAY
from server import send_event

listening = False
clap_count = 0
last_clap_time = 0
last_action_time = 0
current_volume = 0.0

def perform_action(count):
    if count == 1:
        pyautogui.click()
        send_event("action", {"action": "🖱 Left Click"})
    elif count == 2:
        pyautogui.scroll(300)
        send_event("action", {"action": "⬆ Scroll Up"})
    elif count == 3:
        pyautogui.scroll(-300)
        send_event("action", {"action": "⬇ Scroll Down"})

def sound_callback(indata, frames, time_info, status):
    global clap_count, last_clap_time, last_action_time, current_volume
    if not listening:
        return
    volume_norm = float(np.linalg.norm(indata)) * 10.0
    current_volume = volume_norm
    send_event("volume", {"volume": volume_norm})

    if volume_norm > THRESHOLD:
        now = time.time()
        if now - last_clap_time < CLAP_TIMEOUT:
            clap_count += 1
        else:
            clap_count = 1
        last_clap_time = now

    if clap_count > 0 and (time.time() - last_clap_time) > CLAP_TIMEOUT:
        if (time.time() - last_action_time) > ACTION_DELAY:
            perform_action(clap_count)
            last_action_time = time.time()
        clap_count = 0

def listen():
    with sd.InputStream(callback=sound_callback):
        while listening:
            sd.sleep(100)

def start_listening():
    global listening
    if not listening:
        listening = True
        threading.Thread(target=listen, daemon=True).start()
        send_event("status", {"status": "Listening 🎧"})

def stop_listening():
    global listening
    listening = False
    send_event("status", {"status": "Stopped ⛔"})
