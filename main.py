import tkinter
import customtkinter
import os
import threading
import subprocess
import sys
import configparser

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

log_filename = 'log.txt'

def read_log_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return lines


def start_task(label, button):
    config = configparser.ConfigParser()
    #update nn_config for
    try:
        if int(max_packages.get()) < 1 or int(average_speed.get()) < 1 or int(generations.get()) < 1:
            raise
        config['DEFAULT'] = {
            'import_genome' : neural_network.get(),
            'Max_packages': max_packages.get(),
            'average_speed' : average_speed.get(),
            'generations' : generations.get(),
            'option' : switch.get()
        }

        with open('settings.ini' , 'w') as configfile:
            config.write(configfile)

        # Disable the button to prevent multiple starts
        button.configure(state="disabled")
        label.configure(text="Task is running...")
        switch.configure(state="disabled")

        thread = threading.Thread(target= change_values, args = (label,))
        thread.start()
        # Check the thread status periodically
        check_thread_status(thread, label, button)
    except:
        print("plase input correct values")





def change_values(label):
        result = subprocess.Popen([sys.executable, 'traveling_nn.py'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        stdout, stderr = result.communicate()
        
        label.configure(text = "Task Completed")

def check_thread_status(thread, label, button, last_size=0):
    if thread.is_alive():
        # If the thread is still running, check again after 100ms
        current_size = os.path.getsize(log_filename)
        if current_size > last_size:
            with open(log_filename, 'r') as f:
                content = f.read()
                f.seek(last_size)
                new_data = f.read()
                textbox.delete(1.0, tkinter.END)
                textbox.insert(1.0,content)
                textbox.yview_moveto(1)
                print(new_data)  # Or process the new data as needed
        last_size = current_size
    # Adjust the sleep time as needed
        label.after(100, check_thread_status, thread, label, button, last_size)

    else:
        # Re-enable the button when the task is done
        button.configure(state="normal")
        switch.configure(state="normal")
  

def change_page(pagename):
    pass

def create_label_and_entry(label_text,inital_value,row,show=None):
    label = customtkinter.CTkLabel(app,text= label_text)
    label.pack( padx=10, pady=2)
    
    entry = customtkinter.CTkEntry(app, show=show)
    entry.insert(0, inital_value)
    entry.pack(padx=10, pady=2)
    return(label,entry)


#building app  
app = customtkinter.CTk()
app.geometry("740x480")
app.title("Nurel Network Evo")

title = customtkinter.CTkLabel(app, text= "Start Program")
title.pack(padx=10, pady=10) 

#create option box

neural_network_label, neural_network = create_label_and_entry("neural network", "", 0)

switch = customtkinter.CTkSwitch(app, text= "view neural network")
switch.pack()

generations_label , generations = create_label_and_entry("generations", "15", 1)
max_packages_label,max_packages = create_label_and_entry("max packages", "8", 2)
average_speed_label,average_speed = create_label_and_entry("average speed", "20", 3)



Summit_Values = customtkinter.CTkButton(app,text="confirm", command=lambda: start_task(title,Summit_Values))
Summit_Values.pack()    

textbox =customtkinter.CTkTextbox(app, wrap = "word")
textbox.pack(pady = 20,fill = "both", expand=True)

textbox.bind("<Key>", lambda e: "break")
textbox.bind("<Button-1>", lambda e: "break")

scrollbar = customtkinter.CTkScrollbar(textbox,command=textbox.yview)
textbox.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row = 0, column = 1, sticky= "ns")


if __name__ == '__main__':
    
    with open(log_filename, 'w'):
        pass
    app.mainloop()



#create new page