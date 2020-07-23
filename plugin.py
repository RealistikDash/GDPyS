import threading
import os
    
def add_plugins():
    def exec_plugin(code):
        exec(code)
    if not os.path.exists("plugins"):
        os.mkdir("plugins")
    for plugin in os.listdir("plugins"):
        if os.path.isdir("plugins/" + plugin):
            continue
        print(plugin)
        f = open("plugins/" + plugin, "r")
        threading.Thread(target=exec_plugin, args=[f.read()]).start()