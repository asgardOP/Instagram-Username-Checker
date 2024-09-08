import tkinter as tk
from tkinter import scrolledtext
from requests import get as g, post
from random import choices
import string
from threading import Thread, Event
from time import sleep
from tkinter import ttk
from PIL import Image, ImageTk

# Global variable to control the stopping of the username check
stop_event = Event()

def generate_usernames():
    num_users = int(num_users_entry.get() or 0)
    length = int(length_entry.get() or 0)
    generated_usernames = []

    for _ in range(num_users):
        username = ''.join(choices(string.ascii_lowercase + string.digits + '__', k=length))
        generated_usernames.append(username)

    text_area.config(state=tk.NORMAL)
    text_area.delete('1.0', tk.END)
    text_area.insert(tk.END, '\n'.join(generated_usernames))
    text_area.config(state=tk.DISABLED)

def send_telegram_message(user, message):
    bot_token = bot_token_entry.get()
    user_id = user_id_entry.get()
    if bot_token and user_id:
        try:
            response = post(f'https://api.telegram.org/bot{bot_token}/sendMessage', data={
                'chat_id': user_id,
                'text': message
            })
            if response.status_code != 200:
                print(f'Failed to send message: {response.text}')
        except Exception as e:
            print(f'Error sending message: {str(e)}')

def check_usernames():
    usernames = text_area.get("1.0", "end-1c").splitlines()
    total_usernames = len(usernames)
    result_area.config(state=tk.NORMAL)
    result_area.delete('1.0', tk.END)

    def process_username(user, index):
        if stop_event.is_set():
            return
        user = user.strip()
        if not user:
            return
        try:
            response = g(f'https://www.instagram.com/{user}', timeout=10)
            content = response.text
            if user in content:
                place = content.find(user)
                status = 'taken' if place == 1534 else 'free'
                result = f'- {user}: {status}'
                if status == 'free':
                    send_telegram_message(user, f'Username {user} is free!')
            else:
                result = f'- {user}: err: 504'
        except Exception as e:
            result = f'- {user}: error - {str(e)}'

        result_area.insert(tk.END, result + '\n')
        result_area.yview(tk.END)
        result_area.update_idletasks()
        progress['value'] = (index + 1) / total_usernames * 100
        progress.update()
        sleep(1)  # Optional delay between requests

    for index, user in enumerate(usernames):
        if stop_event.is_set():
            break
        app.after(0, process_username, user, index)
        app.update()

def start_checking():
    global stop_event
    stop_event.clear()
    Thread(target=check_usernames).start()

def stop_checking():
    stop_event.set()

def on_enter(e):
    e.widget.config(fg='black')

def on_leave(e):
    e.widget.config(fg='white')

app = tk.Tk()
app.title("Instagram Username Checker")
app.geometry("400x800")
app.minsize(380, 800)
app.maxsize(732, 1200)
app.configure(bg='#f0f0f0')

# Header Frame for Instagram Logo
header_frame = tk.Frame(app, bg='#f0f0f0')
header_frame.pack(pady=10, padx=10, fill=tk.X)

# Instagram Logo
instagram_image = Image.open("instagram_logo.png")
instagram_image = instagram_image.resize((100, 40), Image.LANCZOS)  # Smaller image
instagram_photo = ImageTk.PhotoImage(instagram_image)
instagram_label = tk.Label(header_frame, image=instagram_photo, bg='#f0f0f0')
instagram_label.pack(side=tk.LEFT)

# Frame for inputs
input_frame = tk.Frame(app, bg='#f0f0f0')
input_frame.pack(pady=10, padx=10, fill=tk.X)

tk.Label(input_frame, text="Number of usernames:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', padx=5, pady=5)
num_users_entry = tk.Entry(input_frame, width=20)
num_users_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Length of username letters:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', padx=5, pady=5)
length_entry = tk.Entry(input_frame, width=20)
length_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Telegram bot token (Optional):", bg='#f0f0f0').grid(row=2, column=0, sticky='w', padx=5, pady=5)
bot_token_entry = tk.Entry(input_frame, width=20)
bot_token_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Telegram user ID (Optional):", bg='#f0f0f0').grid(row=3, column=0, sticky='w', padx=5, pady=5)
user_id_entry = tk.Entry(input_frame, width=20)
user_id_entry.grid(row=3, column=1, padx=5, pady=5)

# Buttons Frame
button_frame = tk.Frame(app, bg='#f0f0f0')
button_frame.pack(pady=10, padx=10, fill=tk.X)

generate_button = tk.Button(button_frame, text="Generate Usernames", command=generate_usernames, bg='#4CAF50', fg='white', relief=tk.RAISED, padx=10, pady=5, cursor='hand2')
generate_button.pack(side=tk.LEFT, padx=5)
generate_button.bind("<Enter>", on_enter)
generate_button.bind("<Leave>", on_leave)

check_button = tk.Button(button_frame, text="Start Checking", command=start_checking, bg='#2196F3', fg='white', relief=tk.RAISED, padx=10, pady=5, cursor='hand2')
check_button.pack(side=tk.LEFT, padx=5)
check_button.bind("<Enter>", on_enter)
check_button.bind("<Leave>", on_leave)

stop_button = tk.Button(button_frame, text="Stop Checking", command=stop_checking, bg='#f44336', fg='white', relief=tk.RAISED, padx=10, pady=5, cursor='hand2')
stop_button.pack(side=tk.LEFT, padx=5)
stop_button.bind("<Enter>", on_enter)
stop_button.bind("<Leave>", on_leave)

# Progress Bar
progress = ttk.Progressbar(app, orient=tk.HORIZONTAL, length=700, mode='determinate')
progress.pack(pady=10, padx=10)

# Input Area for Usernames
tk.Label(app, text="Usernames List (you can drop your own list or generate one):", bg='#f0f0f0').pack(pady=5)
text_area = scrolledtext.ScrolledText(app, width=90, height=10, bg='#ffffff', fg='#000000')
text_area.pack(pady=5)

# Results Area
tk.Label(app, text="Results:", bg='#f0f0f0').pack(pady=5)
result_area = scrolledtext.ScrolledText(app, width=90, height=10, bg='#ffffff', fg='#000000', state=tk.DISABLED)
result_area.pack(pady=5)

# Copyright Notice
footer = tk.Label(app, text="© 2024 Asgard | Instagram: @3.9.9.6", bg='#f0f0f0', anchor='e', padx=10, pady=10)
footer.pack(side=tk.BOTTOM, fill=tk.X)

app.mainloop()
