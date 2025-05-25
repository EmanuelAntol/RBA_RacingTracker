import time

class scoreKeeper:
    def __init__ (self, names, cooldown, laps):
        self.laps = laps
        self.cooldown = cooldown
        self.in_progress = False
        self.start_time = 0
        self.end_time = 0
        self.racers = []
        self.racernames = []
        
        for contestant in names:
            self.racers.append(racer(contestant, self.laps))
            self.racernames.append(contestant)

        self.sorted_racers = self.sortRacers(0)

    def raceStartTimer(self):
        start_time = time.time()
        self.end_time = 0
        self.in_progress = True
        print ("Race timer started")

    def raceEndTimer(self):
        end_time = time.time()
        self.in_progress = False
        print("Race timer ended")

    def racePauseTimer(self):
        if self.in_progress:
            self.end_time = time.time()
            self.in_progress = False
        else:
            # Resume: adjust start_time to account for paused duration
            paused_duration = time.time() - self.end_time
            self.start_time += paused_duration
            for racer in self.racers:
                racer.pausAdjust(paused_duration)
            self.end_time = 0
            self.in_progress = True

    def reset(self):
        self.in_progress = False
        self.start_time = 0
        self.end_time = 0
        for racer in self.racers:
            racer.laps = []
            racer.raceDone = False
            racer.start_time = 0
            racer.last_seen = 0

    def raceTime(self):
        if self.in_progress:
            elapsed_time = time.time() - self.start_time

        elif self.end_time != 0:
            elapsed_time = self.end_time - self.start_time
        
        else:
            elapsed_time = 0
        
        return elapsed_time
    
    def lapDone(self, input_text):
        if input_text in self.racernames:
            input = self.racernames.index(input_text)
        else:
            return
        
        if self.in_progress:
            current_time = time.time()
            
            if (self.racers[input].GetLastSeen() + self.cooldown < current_time or self.racers[input].GetLastSeen() == 0):
                self.racers[input].lap(current_time)
                self.sorted_racers = self.sortRacers(0)

            self.racers[input].setLastSeen(current_time)   
    
    def manualLapDone(self, input):
        if input in self.racernames and self.in_progress:
            input = self.racernames.index(input)

            if self.in_progress:
                current_time = time.time()
                self.racers[input].lap(current_time)
                self.sorted_racers = self.sortRacers(0)

            self.racers[input].setLastSeen(current_time)  
                      
    def getLapTime(self, input):
        if input in self.racernames:
            input = self.racernames.index(input)
            return self.racers[input].lapTimes()
        return None
     
    def getAllLapTimes(self):
        if len(self.racers) == 0:
            return None
        
        all_laps = []
        for racer in self.racers:
            all_laps.append(racer.lapTimes())
        return all_laps

    def saveResults(self, filename):
        with open(filename, 'w') as file:
            laps_header = ', '.join([f"Lap {i+1}" for i in range(self.laps)])
            file.write("Racer Name, " + laps_header + "\n")
            for racer in self.racers:
                lap_times = ""
                for time in racer.lapTimes():
                    if time == 0:
                        lap_times += "N/A, "
                    else:
                        minutes, seconds = divmod(int(time), 60)
                        minutes = divmod(minutes, 60)[1]
                        lap_times += (f"{minutes:02}:{seconds:02} ({time}), ")
                
                file.write(f"{racer.getName()}, {lap_times}\n")

           
            for i in range(self.laps+1):
                sorted_racers = self.sortRacers(i)
                if i == 0:
                    file.write("\n\nFinal Results: ")
                    for racer in sorted_racers:
                        minutes, seconds = divmod(int(racer.getTotalTime()), 60)
                        minutes = divmod(minutes, 60)[1]
                        file.write(f"{racer.getName()} - {minutes:02}:{seconds:02}, ")
                else:
                    file.write(f"\n\nResults of lap {i}: ")
                    for racer in sorted_racers:
                        minutes, seconds = divmod(int(racer.lapTimes()[i-1]), 60)
                        minutes = divmod(minutes, 60)[1]
                        file.write(f"{racer.getName()} - {minutes:02}:{seconds:02}, ")
                
    def sortRacers(self, mode):
        if mode == 0:
            temp_racers = self.racers.copy()
            temp_racers.sort(key=lambda r: (-r.lapsDoneCount(), r.getTotalTime()))
        else:
            temp_racers = []
            for racer in self.racers:  
                if racer.lapsDoneCount() >= mode:
                    temp_racers.append(racer)
            temp_racers.sort(key=lambda r: (r.lapTimes()[mode-1]))
                                        
        return temp_racers
        
    def getSortedRacers(self):
        return self.sorted_racers

    def startAllRacers(self):
        for racer in self.racers:
            racer.lap(time.time())
            racer.setLastSeen(time.time())

class racer:
    def __init__ (self, name, lapCount):
        self.lapCount = lapCount
        self.name = name
        self.raceDone = False
        self.last_seen = 0
        self.start_time = 0
        self.laps = []
    
    def GetLastSeen(self):
        return self.last_seen
    
    def setLastSeen(self, current_time):
        self.last_seen = current_time
    
    def lapsDoneCount(self):
        return len(self.laps)
    
    def getName(self):
        return self.name
    
    def getraceDone(self):
        return self.raceDone
    
    def lapTimes(self):
        temp_laps = self.laps.copy()
        if self.lapsDoneCount() < self.lapCount:
            temp_laps.extend([0] * (self.lapCount - self.lapsDoneCount()))
        return temp_laps
    
    def pausAdjust(self, duration):
        if self.start_time != 0:
            self.start_time += duration

    def lap(self, current_time):
        if self.raceDone:
            return None
        

        if self.start_time == 0:
            self.start_time = current_time
            print(f"Racer {self.name} started the race")
        else:
            lap_time = current_time - self.start_time
            self.laps.append(lap_time)
            self.start_time = current_time
            print(f"Racer {self.name} completed a lap")

        if self.lapsDoneCount() == self.lapCount:
            self.raceDone = True
            print(f"Racer {self.name} finished")

    def getTotalTime(self):
        return sum(self.lapTimes())

if __name__ == "__main__":
    keeper = scoreKeeper(["Racer 1", "Racer 2", "Racer 3"], cooldown=0.5, laps=3)
    keeper.raceStartTimer()
    keeper.lapDone("Racer 1")
    time.sleep(2)
    keeper.racePauseTimer()
    time.sleep(5)
    keeper.racePauseTimer()
    time.sleep(2)
    keeper.lapDone("Racer 1")
    keeper.lapDone("Racer 1")
    keeper.lapDone("Racer 2")
    time.sleep(1)
    keeper.lapDone("Racer 2")
    keeper.saveResults("score.csv")
    for r in keeper.sortRacers(1):
        print(f"{r.getName()}: {r.laps} {r.lapsDoneCount()} laps done, total time: {r.getTotalTime()} seconds")
