import reader
import score
import tkinter as tk
from tkinter import ttk
import time

def Panels():
    global controlPanel
    controlPanel = tk.Tk()
    controlPanel.title("Control Panel")
    controlPanel.geometry("300x300")

    global scorePanel
    scorePanel = tk.Toplevel(controlPanel)
    scorePanel.title("Score Panel")
    scorePanel.geometry("300x300")

    global timer_label1
    timer_label1 = ttk.Label(controlPanel, text="00:00", font=("Segoe UI", 30))
    timer_label1.pack(pady=20)

    start_button = ttk.Button(controlPanel, text="Start", command=lambda: start_timer())
    start_button.pack(side=tk.LEFT, padx=20)

    global pause_button
    pause_button = ttk.Button(controlPanel, text="Pause", command=lambda: pause_timer())
    pause_button.pack(side=tk.RIGHT, padx=20)
    
    reset_button = ttk.Button(controlPanel, text="Reset", command=lambda: reset_timer())
    reset_button.pack(side=tk.BOTTOM, pady=20)

    global capture_button
    capture_button = ttk.Button(controlPanel, text="Capture", command=lambda: capture_toggle())
    capture_button.pack(side=tk.TOP, pady=20)

    global timer_label2
    timer_label2 = ttk.Label(scorePanel, text="00:00", font=("Segoe UI", 30))
    timer_label2.pack(pady=20)

    global team_list
    team_list = ttk.Label(scorePanel, text="", font=("Segoe UI", 30))
    team_list.pack(pady=20)
    

    controlPanel.mainloop()

def update():
    if running:
        update_score()

        capture_data = capture_update()
        if capture_data:
                keeper.lapDone(capture_data)
            
        controlPanel.after(10, update)

def update_score():
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    minutes = divmod(minutes, 60)[1]
    timer_label1.config(text=f"{minutes:02}:{seconds:02}")
    timer_label2.config(text=f"{minutes:02}:{seconds:02}")

    temp_text = ""
    for racer in keeper.getSortedRacers():
        minutes, seconds = divmod(int(racer.getTotalTime()), 60)
        minutes = divmod(minutes, 60)[1]
        temp_text += f"{racer.getName()}: {minutes:02}:{seconds:02}\n"
    team_list.config(text = temp_text)

def capture_update():
    global capture
    capture_data = None
    if capture:
        capture_data = qr_detector.capture()

        if not running:
            print(f"QR Code Data: {capture_data}")
            controlPanel.after(10, capture_update)
    return(capture_data)
    
def start_timer():
    global running, start_time
    if not running:
        running = True
        start_time = time.time()
        keeper.raceStartTimer()
        update()

def pause_timer():
    global running, start_time, elapsed_time
    
    if running == True:
        running = False
        elapsed_time = time.time() - start_time
        pause_button.config(text="Resume")
        keeper.racePauseTimer()
    elif elapsed_time > 0:
        running = True
        start_time = time.time() - elapsed_time
        pause_button.config(text="Pause")
        keeper.racePauseTimer()
        update()
    
def reset_timer():
    global start_time, running, elapsed_time
    running = False
    timer_label1.config(text="00:00")
    timer_label2.config(text="00:00")
    pause_button.config(text="Pause")
    elapsed_time = 0
    start_time = 0
    keeper.reset()
    
def capture_toggle():
    global capture
    if capture == False:
        capture = True
        capture_button.config(text="Stop Capture")
        if not running:
            capture_update()
        print ("Capture started")

    else:
        capture = False
        capture_button.config(text="Start Capture")
        print ("Capture stopped")

teams = ["5", "https://robotickybattle.sk/", "Team C", "Team D", "Team E", "Team F", "Team G", "Team H"]
keeper = score.scoreKeeper(teams, 3, 5)

capture = False
running = False
start_time = 0
elapsed_time = 0
qr_detector = reader.QRCodeDetector()

Panels()
keeper.saveResults("score1.csv")




    

