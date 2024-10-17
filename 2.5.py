import subprocess
import re
import platform
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import random
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def read_networks_from_cmd():
    p = subprocess.Popen("netsh wlan show networks mode=bssid", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read().decode('utf-8', errors='ignore').strip()
    if platform.system() == 'Windows':
        networks = re.findall(r'SSID\s*\d+\s*:\s*([^\r\n]+).*?Signal\s*:\s*(\d+)%', out, re.DOTALL)
        return networks
    else:
        raise Exception('Unsupported platform')

networks_data = {}
colors = {}

def update(frame):
    global networks_data, colors
    networks = read_networks_from_cmd()
    current_time = datetime.now().strftime('%H:%M:%S')
    
    if not networks_data:
        for ssid, signal_strength in networks:
            networks_data[ssid] = {'x': [], 'y': []}
            colors[ssid] = (random.random(), random.random(), random.random())

    for ssid, signal_strength in networks:
        if ssid not in networks_data:
            networks_data[ssid] = {'x': [], 'y': []}
            colors[ssid] = (random.random(), random.random(), random.random())
        networks_data[ssid]['x'].append(current_time)
        networks_data[ssid]['y'].append(int(signal_strength))
    ax.clear()
    for ssid, data in networks_data.items():
        ax.plot(data['x'], data['y'], label=ssid, color=colors[ssid])
    
    ax.set_ylim(0, 100)
    ax.set_xlim(max(0, frame - 50), frame + 10) 
    ax.set_title("Available Networks")
    ax.set_xlabel("Time")
    ax.set_ylabel("Signal Strength (%)")
    ax.legend(loc='upper right')
    ax.grid(False)



def get_best():
    networks=read_networks_from_cmd()
    if not networks:
        return None
    best_wifi=max(networks,key=lambda x:int(x[1]))
    best_ssid,best_signal=best_wifi
    return(best_ssid.strip())


def connect ():
    ssid=get_best()
    process=subprocess.Popen(f"netsh wlan connect name={ssid}",stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,error=process.communicate()
    global Alert
    Alert.delete(1.0,END)
    if process.returncode==0:
        result=f"successfully connected to {ssid}"
        Alert.insert(1.0,result)
        Alert.pack(fill=BOTH,expand=True)
    else :
        result=f"Error connecting to {ssid}: {error.decode('utf-8')}"
        Alert.insert(1.0,result)
        Alert.pack(fill=BOTH,expand=True)


root = Tk()
root.title("Wi-Fi Signal Strength Monitor")
Alert=Text(root,height=5,width=50)
figure, ax = plt.subplots()
canvas = FigureCanvasTkAgg(figure, master=root)
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
MyButton = Button(root, text="Connect to the best Wi-Fi",command=connect)
MyButton.pack(side=BOTTOM)
animation = FuncAnimation(figure, update, interval=1000)
root.mainloop()
