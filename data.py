from asciimatics.screen import Screen
import render as rd
import datetime

class Graph:
    def __init__(self, screen: Screen, step : int = 60) -> None:

        self.step : int = step
        self.data : dict = {}
        
        self.screen : Screen = screen
        
        return
    
    def add_data(self, d: dict) -> None:
        
        time : datetime.datetime = datetime.datetime.strptime(d['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        seconds_time : float = (time - datetime.datetime(1970,1,1)).total_seconds()
        minute_time : int = int(seconds_time // self.step * self.step)
        
        current_time : list = []
        
        if minute_time in self.data.keys():
            current_time = self.data[minute_time]
        elif minute_time - self.step in self.data.keys() and len(self.data[minute_time - self.step]) != 0:
            current_time = [self.data[minute_time - self.step][-1]]

        current_time.append(float(d["price"]))
        
        self.data[minute_time] = current_time
        
        return
    
    def calc_OCHL(self, time : int) -> dict[str, float]:
        
        try:
            data = self.data[time]
            if len(data) == 0: return {}
        except:
            return {}
        
        ohcl = {
            'open' : data[0],
            'close' : data[-1],
            'high' : max(data),
            'low' : min(data)
        }
        
        return ohcl
    
    def render_data(self) -> None:
        
        clear_data = {}
        
        for time in self.data:
            clear_data[time] = self.calc_OCHL(time)
                
        rd.render_data(self.screen, clear_data)
        
        return
    