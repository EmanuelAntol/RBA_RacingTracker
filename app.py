import score
import tkinter as tk
from tkinter import ttk
import time

capture = False
running = False
start_time = 0
elapsed_time = 0
qr_detector = None
saved = True
paused = False
cooldown = 5
laps = 3
teams = ["Team A", "Team B", "Team C"]
savename = "score.csv"


try :
    with open("conf.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("COOLDOWN"):
                cooldown = int(line.split("=")[1].strip())
            elif line.startswith("LAPS"):
                laps = int(line.split("=")[1].strip())
            elif line.startswith("TEAMS"):
                teams = line.split("=")[1].strip().split(",")
                teams = [team.strip() for team in teams]
            elif line.startswith("SAVENAME"):
                savename = line.split("=")[1].strip()
except:
    pass               


def Panels():
    global controlPanel, begin_with_start, scorePanel, timer_label1, timer_label2, team_list, start_button, pause_button, capture_button, save_button, enter_button, input_text_listbox, teams
    controlPanel = tk.Tk()
    controlPanel.title("Racing control panel")
    controlPanel.resizable(False, False)
    
    scorePanel = tk.Toplevel(controlPanel)
    scorePanel.title("Score Panel")

    text_frame = ttk.Frame(controlPanel)
    text_frame.pack(pady=10,side=tk.BOTTOM, fill=tk.X)

    button_frame = ttk.Frame(controlPanel)
    button_frame.pack(pady=10, side=tk.BOTTOM, fill=tk.X, padx=10)

    
    
    start_button = ttk.Button(button_frame, text="Start", command=lambda: start_timer())
    start_button.grid(row=0, column=0, padx=5, pady=5)

    begin_with_start = tk.BooleanVar(value=True)
    begin_with_start_check = ttk.Checkbutton(button_frame, text="Begin with Start", variable=begin_with_start, onvalue=True, offvalue=False)
    begin_with_start_check.grid(row=0, column=4, padx=5, pady=5)
    
    
    pause_button = ttk.Button(button_frame, text="Pause", command=lambda: pause_timer())
    pause_button.grid(row=0, column=1, padx=5, pady=5)

    reset_button = ttk.Button(button_frame, text="Reset", command=lambda: reset_timer())
    reset_button.grid(row=0, column=2, padx=5, pady=5)

    capture_button = ttk.Button(button_frame, text="Start Capture", command=lambda: capture_toggle())
    capture_button.grid(row=2, column=0, pady=5, padx= 5,  sticky="ew")

    save_button = ttk.Button(button_frame, text="Save", command=lambda: save_results())
    save_button.grid(row=2, column=1, pady=5, padx= 5, sticky="ew")
    
    timer_label1 = ttk.Label(controlPanel, text="00:00", font=("Segoe UI", 30))
    timer_label1.pack(pady=20)

    
    input_text_listbox = ttk.Combobox(text_frame, values=teams, width=20)
    input_text_listbox.pack(pady=10, side=tk.LEFT, padx=10)
    input_text_listbox.set("Select Racer")
    input_text_listbox.bind("<Return>", lambda event: keeper.manualLapDone(input_text_listbox.get()))


    enter_button = ttk.Button(text_frame, text="Enter", command=lambda: keeper.manualLapDone(input_text_listbox.get()))
    enter_button.pack(pady=10, side=tk.RIGHT, padx=10)
    

    timer_label2 = ttk.Label(scorePanel, text="00:00", font=("Segoe UI", 30))
    timer_label2.pack(pady=20)


    team_list = ttk.Label(scorePanel, text="", font=("Segoe UI", 30))
    team_list.pack(pady=20)
    

    controlPanel.mainloop()

def update():
    global saved
    if running:
        saved = False
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
    global running, start_time, begin_with_start
    if not running:
        reset_timer()
        running = True
        start_button.config(text="Stop")
        start_time = time.time()
        keeper.raceStartTimer()
        if begin_with_start.get():
            keeper.startAllRacers()
        update()
    else:
        running = False
        start_button.config(text="Start")
        elapsed_time = time.time() - start_time
        keeper.raceEndTimer()
        update_score()

def pause_timer():
    global running, start_time, elapsed_time, paused
    
    if running == True:
        running = False
        paused = True
        elapsed_time = time.time() - start_time
        pause_button.config(text="Resume")
        keeper.racePauseTimer()
    elif elapsed_time > 0 and paused == True:
        running = True
        start_time = time.time() - elapsed_time
        pause_button.config(text="Pause")
        keeper.racePauseTimer()
        update()
    
def reset_timer():
    global start_time, running, elapsed_time, saved
    if not saved:
        keeper.saveResults("ResetAutosave.csv")
    running = False
    saved = True
    timer_label1.config(text="00:00")
    timer_label2.config(text="00:00")
    pause_button.config(text="Pause")
    start_button.config(text="Start")
    
    elapsed_time = 0
    start_time = 0
    keeper.reset()
    team_list.config(text = "")
    
    
def capture_toggle():
    import reader
    global capture, qr_detector

    if qr_detector == None:
        qr_detector = reader.QRCodeDetector()

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

def save_results():
    global savename, saved
    keeper.saveResults(savename)
    saved = True

try:
    keeper = score.scoreKeeper(teams, cooldown, laps)
    Panels()
finally:
    if not saved:
        keeper.saveResults("ExitAutosave.csv")




    

