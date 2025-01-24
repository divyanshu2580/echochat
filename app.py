import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk , ImageDraw
import psycopg2
import hashlib
import os
from datetime import datetime , timedelta
import webbrowser
from dotenv import load_dotenv , dotenv_values
load_dotenv()


connection = psycopg2.connect(
    dbname="testing",
    user="postgres",
    password= os.getenv("PASSWORD"),
    host="localhost",
    port="5432"
)

cursor = connection.cursor()

root = tk.Tk()
root.geometry('1200x750+0+0')
root.title("Echo Chat")
root.iconbitmap("images/icon.ico")

container = tk.Frame(root)
container.pack(fill="both", expand=True)

login_frame = tk.Frame(container)
signup_frame = tk.Frame(container)
home_frame = tk.Frame(container)
contacts_profile_frame = tk.Frame(container)
settings_frame = tk.Frame(container)
profile_frame = tk.Frame(container)
add_contacts_frame = tk.Frame(container)
help_frame = tk.Frame(container)
block_contact_frame = tk.Frame(container)
unblock_contact_frame = tk.Frame(container)

for frame in (login_frame,signup_frame,contacts_profile_frame,home_frame,settings_frame,profile_frame,add_contacts_frame,help_frame,block_contact_frame,unblock_contact_frame):
    frame.grid(row=0,column=0 , sticky='nsew')

# images

image_path = "images/logo.png"  
image = Image.open(image_path)
image = image.resize((500, 100), Image.LANCZOS)  
logo_image = ImageTk.PhotoImage(image)

image_path1 = "images/background.png"  
image_bg = Image.open(image_path1)
image_bg = image_bg.resize((550,550), Image.LANCZOS)  
background_image = ImageTk.PhotoImage(image_bg)

image_path2 = "images/back.jpg"
image_back2 = Image.open(image_path2)
image_back2 = image_back2.resize((1200,750), Image.LANCZOS)
back_image_app = ImageTk.PhotoImage(image_back2)

image_path3 = "images/forward.png"
image_back3 = Image.open(image_path3)
image_back3 = image_back3.resize((30,30), Image.LANCZOS)
forward_image= ImageTk.PhotoImage(image_back3)

image_path4 = "images/attach.png"
image_back4 = Image.open(image_path4)
image_back4 = image_back4.resize((30,30), Image.LANCZOS)
attach_image= ImageTk.PhotoImage(image_back4)

image_path5 = "images/settings.png"
image_back5 = Image.open(image_path5)
image_back5 = image_back5.resize((30,30), Image.LANCZOS)
settings_image = ImageTk.PhotoImage(image_back5)

image_path6 = "images/help.png"
image_back6 = Image.open(image_path6)
image_back6 = image_back6.resize((30,30), Image.LANCZOS)
help_image = ImageTk.PhotoImage(image_back6)

image_path7 = "images/add_contact.png"
image_back7 = Image.open(image_path7)
image_back7 = image_back7.resize((30,30), Image.LANCZOS)
add_contact_image = ImageTk.PhotoImage(image_back7)

image_path8 = "images/edit.png"
image_back8 = Image.open(image_path8)
image_back8 = image_back8.resize((20,20), Image.LANCZOS)
edit_image = ImageTk.PhotoImage(image_back8)

profile_pic_path = ""  
current_user_id = None
contact_images = [] 
image_refs=[]
contact_user_id = None
block_contact_images = []
unblock_contact_images = []  
global messages_text

# functions 

def show_frame(frame):
    frame.tkraise()

def add_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry['fg'] = 'grey'

def remove_placeholder(event, placeholder):
    if event.widget.get() == placeholder:
        event.widget.delete(0, tk.END)
        event.widget['fg'] = 'black'

def restore_placeholder(event, placeholder):
    if event.widget.get() == '':
        add_placeholder(event.widget, placeholder)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def format_last_seen(last_seen):
    now = datetime.now()
    
    if isinstance(last_seen, datetime):
        last_seen_date = last_seen
    elif isinstance(last_seen, str):
        try:
            last_seen_date = datetime.strptime(last_seen, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Long time ago"
    else:
        return "Long time ago"
    
    delta = now - last_seen_date
    
    if delta.days == 0:
        return last_seen_date.strftime("Today at %H:%M")
    elif delta.days == 1:
        return last_seen_date.strftime("Yesterday at %H:%M")
    elif delta.days < 7:
        return last_seen_date.strftime("%A at %H:%M")
    else:
        return last_seen_date.strftime("%Y-%m-%d at %H:%M")

def login_user():
    global current_user_id
    try:
        email = email_entry_login.get()
        password = hash_password(password_entry_login.get())
        
        cursor.execute("SELECT user_id, profile_picture FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        
        if user:
            current_user_id = user[0]
            profile_picture_path = user[1]
            
            cursor.execute("UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE user_id = %s", (current_user_id,))
            connection.commit()
            
            messagebox.showinfo("Success", "Login successful!")
            load_contacts()
            display_profile_picture(canvas_nav_bar, profile_picture_path, 20,5)  
            show_frame(home_frame)
        else:
            messagebox.showerror("Error", "Invalid email or password.")
    except Exception as e:
        print(f"Exception occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def open_profile_frame():
    show_frame(profile_frame)

def register_user():
    global current_user_id, profile_pic_path
    try:
        email = email_entry_signup.get()
        name = uname_entry_signup.get()
        password = hash_password(password_entry_signup.get())

        if not profile_pic_path:
            profile_pic_path = 'C:/Users/user/OneDrive/Desktop/messenger/images/user.png'

        query = "INSERT INTO users (email, username, password, profile_picture) VALUES (%s, %s, %s, %s) RETURNING user_id"      

        cursor.execute(query, (email, name, password, profile_pic_path))
        current_user_id = cursor.fetchone()[0]
        connection.commit()
        
        messagebox.showinfo("Success", "Account created successfully!")

        email_entry_signup.delete(0, tk.END)
        uname_entry_signup.delete(0, tk.END)
        password_entry_signup.delete(0, tk.END)
        profile_pic_path = None  
        
        show_frame(login_frame)

    except Exception as e:
        print(f"Exception occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def update_navbar_profile_picture():
    global profile_button
    try:
        cursor.execute("SELECT profile_picture FROM users WHERE user_id = %s", (current_user_id,))
        profile_picture_path = cursor.fetchone()[0]

        if profile_picture_path and os.path.exists(profile_picture_path):
            img = Image.open(profile_picture_path)
        else:
            img = Image.open('C:/Users/user/OneDrive/Desktop/messenger/images/user.png')

        img = img.resize((50, 50), Image.LANCZOS)
        img = circular_image(img)
        img_tk = ImageTk.PhotoImage(img)

        if profile_button:
            profile_button.destroy()

        profile_button = tk.Button(nav_bar_frame, image=img_tk, command=open_profile_frame, background="lavender", border=0)
        profile_button.image = img_tk
        profile_button.place(x=20, y=5)

    except Exception as e:
        print(f"Error updating navbar profile picture: {e}")

def display_profile_picture(canvas, profile_picture_path, x=20, y=5):
    global image_refs
    image_refs = []  # Ensure image_refs is re-initialized to avoid overflow

    try:
        img = Image.open(profile_picture_path)
        img = img.resize((50, 50), Image.LANCZOS)
        img = circular_image(img)
        img_tk = ImageTk.PhotoImage(img)

        image_refs.append(img_tk)
        canvas.delete("profile_picture")

        button = tk.Button(canvas, image=img_tk, command=open_profile_frame, background="lavender", border=0)

        # Place the button with fixed coordinates and prevent shifting
        canvas.create_window(x, y, anchor='nw', window=button, tags="profile_picture")
        canvas.update_idletasks()

    except Exception as e:
        print(f"Error loading profile picture: {e}")
        # Load default image if there's an error
        default_img = Image.open('C:/Users/user/OneDrive/Desktop/messenger/images/user.png')
        default_img = default_img.resize((50, 50), Image.LANCZOS)
        default_img = circular_image(default_img)
        default_img_tk = ImageTk.PhotoImage(default_img)
        image_refs.append(default_img_tk)
        
        button = tk.Button(canvas, image=default_img_tk, command=open_profile_frame, background="lavender", border=0)
        canvas.create_window(x, y, anchor='nw', window=button, tags="profile_picture")
        canvas.update_idletasks()

def circular_image(image):
    mask = Image.new("L", (image.size[0], image.size[1]), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.size[0], image.size[1]), fill=255)
    result = image.copy()
    result.putalpha(mask)
    return result

def load_contacts():
    global contact_images
    contacts_canvas.delete("all")
    contact_images = []

    cursor.execute("""
        SELECT U.user_id, COALESCE(C.contact_name, U.username) AS display_name, U.profile_picture,
               COALESCE(MAX(M.time_stamp), '2024-01-01') AS last_message_time,
               COALESCE(SUM(CASE WHEN M.receiver_id = %s AND M.read = FALSE THEN 1 ELSE 0 END), 0) AS unread_count,
               C.status
        FROM contacts C
        JOIN users U ON U.user_id = C.contact_user_id
        LEFT JOIN messages M ON (M.sender_id = C.contact_user_id AND M.receiver_id = C.user_id)
        WHERE C.user_id = %s
        GROUP BY U.user_id, display_name, U.profile_picture, C.status
        ORDER BY last_message_time DESC NULLS LAST
    """, (current_user_id, current_user_id))

    contacts = cursor.fetchall()
    y = 10
    default_image_path = 'C:/Users/user/OneDrive/Desktop/messenger/images/user.png'

    for contact in contacts:
        # print(contact)  # Debugging: Print the contact tuple to check its structure
        
        try:
            contact_user_id = contact[0]
            contact_name = contact[1]
            profile_picture_path = contact[2] if contact[2] else default_image_path
            last_message_time = contact[3]
            unread_count = contact[4]
            status = contact[5]  # Adjusted to index 5 instead of 6

            # Determine the most recent message time (sent or received)
            if last_message_time:
                current_date = datetime.now()
                if last_message_time.date() == current_date.date():
                    last_message_display = last_message_time.strftime('%H:%M')  # Show time for today
                elif last_message_time.date() == (current_date - timedelta(days=1)).date():
                    last_message_display = "Yesterday"  # Show 'Yesterday'
                else:
                    last_message_display = last_message_time.strftime('%d/%m/%Y')  # Show date for older messages
            else:
                last_message_display = ""  # No message time

            if profile_picture_path and os.path.exists(profile_picture_path):
                try:
                    img = Image.open(profile_picture_path)
                    img = img.resize((50, 50), Image.LANCZOS)
                    img = circular_image(img)
                    img_tk = ImageTk.PhotoImage(img)
                    contacts_canvas.create_image(35, y + 25, image=img_tk, anchor="center")
                    contact_images.append(img_tk)
                except Exception as e:
                    messagebox.showerror("Error", f"Error loading image: {e}")
            else:
                messagebox.showerror("Error", f"Profile picture not found at {profile_picture_path}")

            # Display contact name
            contact_name_id = contacts_canvas.create_text(90, y + 15, text=contact_name, anchor="w", font=("Arial", 12))
            
            # Display last message time next to the name
            contacts_canvas.create_text(300, y + 15, text=last_message_display, anchor="center", font=("Arial", 10, "italic"))

            # Handle status and unread count
            if status == "blocked":
                contacts_canvas.create_oval(300, y + 10, 320, y + 30, fill="red", outline="red")
                contacts_canvas.create_text(310, y + 20, text="Blocked", fill="white", font=("Arial", 10, "bold"))
                contacts_canvas.itemconfig(contact_name_id, fill="gray")
            else:
                if unread_count > 0:
                    unread_text = f"{unread_count} unread message(s)"
                    contacts_canvas.create_text(90, y + 35, text=unread_text, anchor="w", font=("Arial", 10, "bold"), fill="green")

            # Add click event for contact selection
            contacts_canvas.tag_bind(contact_name_id, "<Button-1>", lambda e, user_id=contact_user_id, status=status: on_contact_select(user_id, status))

            y += 60
        except IndexError as e:
            # print(f"Error accessing contact data: {e}")
            continue  # Skip this contact if there's an issue with accessing the data

    contacts_canvas.update_idletasks()
    contacts_canvas.config(scrollregion=contacts_canvas.bbox("all"))

def on_contact_select(user_id, status):
    global contact_user_id
    contact_user_id = user_id

    if status == "blocked":
        messagebox.showwarning("Blocked", "You cannot send messages to this contact.")
    else:
        show_chat_screen(user_id)

def get_user_email(user_id):
    cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else "Unknown"
    
def attach_file():
    if contact_user_id is None:
        messagebox.showwarning("No Contact Selected", "Please select a contact before attaching a file.")
        return

    # Check if the selected contact has blocked the current user
    cursor.execute("SELECT status FROM contacts WHERE user_id = %s AND contact_user_id = %s", 
                   (contact_user_id, current_user_id))
    result = cursor.fetchone()
    update_navbar_profile_picture()    

    if result and result[0] == "blocked":  # If current user is blocked by the contact
        messagebox.showwarning("Blocked", "You have been blocked by this contact. You cannot send files.")
        return

    file_types = [("Image Files", "*.jpg *.jpeg *.png"), ("PDF Files", "*.pdf"), ("Excel Files", "*.xlsx")]
    file_path = filedialog.askopenfilename(filetypes=file_types)

    if file_path:
        file_name = os.path.basename(file_path)
        file_type = file_path.split('.')[-1].lower()

        try:
            # Insert a message record into the messages table with an empty message content
            cursor.execute("""
                INSERT INTO messages (sender_id, receiver_id, time_stamp, created_at, read) 
                VALUES (%s, %s, NOW(), NOW(), FALSE)
            """, (current_user_id, contact_user_id))
            connection.commit()

            # Retrieve the last inserted message_id
            cursor.execute("SELECT currval(pg_get_serial_sequence('messages','message_id'))")
            message_id = cursor.fetchone()[0]

            if message_id:
                # Insert file details into the attachments table
                cursor.execute("INSERT INTO attachments (message_id, file_path, file_type) VALUES (%s, %s, %s)",
                               (message_id, file_path, file_type))
                connection.commit()

                # Load the chat history, ensuring you pass the required arguments
                load_chat_history(messages_text, contact_user_id)

        except Exception as e:
            connection.rollback()  # Rollback in case of error
            messagebox.showerror("Error", f"An error occurred while sending the file: {e}")

def display_attachment(file_name, file_path):
    if contact_user_id is None:
        messagebox.showwarning("No Contact Selected", "Please select a contact before sending a file.")
        return

    # Check if the contact is blocked
    cursor.execute("SELECT status FROM contacts WHERE user_id = %s AND contact_user_id = %s", (current_user_id, contact_user_id))
    result = cursor.fetchone()

    if result and result[0] == "blocked":  # If contact is blocked
        messagebox.showwarning("Blocked", "You cannot display files to this contact.")
        return

    try:
        # Define max width and height for the images
        max_width = 300
        max_height = 300

        # Handle file attachment based on file type
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Display image
            with Image.open(file_path) as img:
                img.thumbnail((max_width, max_height))
                image = ImageTk.PhotoImage(img)
                messages_text.image_create(tk.END, image=image)  # Insert image into text widget
                messages_text.insert(tk.END, f"\nFile attached: {file_name}\n", 'timestamp')
                image_refs.append(image)  # Keep a reference to avoid garbage collection

        elif file_path.lower().endswith('.pdf'):
            # Display PDF (Placeholder: add actual PDF viewer logic if needed)
            attachment_message = f"PDF attached: {file_name}"
            messages_text.insert(tk.END, f"{attachment_message}\n", 'timestamp')

        else:
            # Display other file types
            attachment_message = f"File attached: {file_name}"
            messages_text.insert(tk.END, f"{attachment_message}\n", 'timestamp')

        # Scroll to the bottom of the text widget to show the new attachment
        messages_text.yview(tk.END)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while displaying the attachment: {e}")

def clear_screen(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def show_chat_screen(contact_user_id):
    global messages_text

    try:
        clear_screen(chat_frame)
        clear_screen(chat_name_frame)

        chat_frame.config(width=780, height=700)
        chat_name_frame.config(height=80)

        # Fetch contact information
        cursor.execute("""
            SELECT contact_name, last_seen, profile_picture  
            FROM contacts C  
            JOIN users U ON U.user_id = C.contact_user_id  
            WHERE C.user_id = %s AND C.contact_user_id = %s
        """, (current_user_id, contact_user_id))

        result = cursor.fetchone()

        if result:
            contact_name, last_seen, profile_picture_path = result
        else:
            contact_name = "Unknown"
            last_seen = "offline"
            profile_picture_path = None

        formatted_last_seen = format_last_seen(last_seen)

        def open_contact_profile_page():
            show_contact_profile_page(contact_user_id)

        # Handle profile picture display
        if profile_picture_path and os.path.exists(profile_picture_path):
            try:
                img = Image.open(profile_picture_path)
                img = img.resize((60, 60), Image.LANCZOS)
                img = circular_image(img)
                img_tk = ImageTk.PhotoImage(img)
                image_refs.append(img_tk)
                profile_button = tk.Button(chat_name_frame, image=img_tk, command=open_contact_profile_page, background="lavender", borderwidth=0)
                profile_button.image = img_tk
                profile_button.pack(side="left", padx=10)
            except Exception as e:
                print(f"Error loading chat image: {e}")
                # Use default image if there's an error
                default_img = Image.open('C:/Users/user/OneDrive/Desktop/messenger/images/user.png')
                default_img = default_img.resize((60, 60), Image.LANCZOS)
                default_img = circular_image(default_img)
                default_img_tk = ImageTk.PhotoImage(default_img)
                image_refs.append(default_img_tk)
                profile_button = tk.Button(chat_name_frame, image=default_img_tk, command=open_contact_profile_page, background="lavender", borderwidth=0)
                profile_button.image = default_img_tk
                profile_button.pack(side="left", padx=10)
        else:
            # Use default image if profile picture is not available
            default_img = Image.open('C:/Users/user/OneDrive/Desktop/messenger/images/user.png')
            default_img = default_img.resize((60, 60), Image.LANCZOS)
            default_img = circular_image(default_img)
            default_img_tk = ImageTk.PhotoImage(default_img)
            image_refs.append(default_img_tk)
            profile_button = tk.Button(chat_name_frame, image=default_img_tk, command=open_contact_profile_page, background="lavender", borderwidth=0)
            profile_button.image = default_img_tk
            profile_button.pack(side="left", padx=10)

        tk.Label(chat_name_frame, text=f"{contact_name}", background="lavender", fg="midnightblue", font=("futura", 20, "bold")).pack(side="left", padx=10, pady=5)
        tk.Label(chat_name_frame, text=f"Last seen: {formatted_last_seen}", background="lavender", fg="gray", font=("futura", 12)).pack(side="left", padx=10)

        messages_text = tk.Text(chat_frame, wrap=tk.WORD, background="lavender", width=100, height=35)
        messages_text.pack(fill='both', expand=True)

        load_chat_history(messages_text, contact_user_id)

        # Mark messages as read
        cursor.execute("""
            UPDATE messages SET read = TRUE 
            WHERE sender_id = %s AND receiver_id = %s AND read = FALSE
        """, (contact_user_id, current_user_id))

        # Commit the transaction
        connection.commit()

        load_contacts()

    except Exception as e:
        # Rollback in case of any exception
        connection.rollback()
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

    # Update navbar profile picture after showing chat screen
    update_navbar_profile_picture()


def send_message(message, message_entry):
    global contact_user_id, messages_text

    try:
        cursor.execute("""
            SELECT status
            FROM contacts
            WHERE user_id = %s AND contact_user_id = %s
        """, (current_user_id, contact_user_id))
        contact_status = cursor.fetchone()

        if contact_status and contact_status[0] == 'blocked':
            messagebox.showwarning("Blocked", "You have blocked this contact.")
            return 

        cursor.execute("""
            SELECT status
            FROM contacts
            WHERE user_id = %s AND contact_user_id = %s
        """, (contact_user_id, current_user_id))
        reverse_status = cursor.fetchone()

        if reverse_status and reverse_status[0] == 'blocked':
            messagebox.showwarning("Blocked", "This contact has blocked you.")
            return  

        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, contents, time_stamp)
            VALUES (%s, %s, %s, NOW())
        """, (current_user_id, contact_user_id, message))

        connection.commit()
        text_entry_chat.delete(0,tk.END)

        load_chat_history(messages_text, contact_user_id)
        update_navbar_profile_picture()

    except Exception as e:
        # Rollback the transaction in case of an error
        connection.rollback()
        # Display the actual error message for debugging
        messagebox.showerror("Error", f"An error occurred: {e}")

def format_timestamp(timestamp):
    if timestamp is None:
        return "N/A"  
    return timestamp.strftime("%Y-%m-%d at %H:%M")

def update_last_seen():
    now = datetime.now()
    try:
        cursor.execute("UPDATE users SET last_seen = %s WHERE user_id = %s", (now, current_user_id))
        connection.commit()  
    except Exception as e:
        connection.rollback() 

def on_closing():
    update_last_seen()  
    root.destroy()  

def update_contact_name(contact_user_id, new_name):
    cursor.execute("UPDATE contacts SET contact_name = %s WHERE user_id = %s AND contact_user_id = %s ", (new_name, current_user_id, contact_user_id))
    connection.commit()
    show_contact_profile_page(contact_user_id)

def change_contact_name(contact_user_id):
    change_name_frame = tk.Toplevel(background="lavender")
    change_name_frame.title("Change Contact Name")
    change_name_frame.iconbitmap("images/icon.ico")

    tk.Label(change_name_frame, text=" New Contact Name ",fg="midnightblue",bg="lavender", font=("futura", 20,"bold")).pack(pady=10)
    entry_new_name = tk.Entry(change_name_frame,bg="lavender", fg="midnightblue",border=5,font=("futura", 15), width=20)
    entry_new_name.pack(pady=10,padx=10)

    def on_change_click():
        new_name = entry_new_name.get()
        if new_name:
            update_contact_name(contact_user_id, new_name)
            change_name_frame.destroy()
            load_contacts()
        else:
            messagebox.showerror("Error", "Name cannot be empty.")

    tk.Button(change_name_frame,border=5, text="CHANGE", font=("futura", 16,"bold"),bg="lavender", fg="midnightblue", command=on_change_click).pack(pady=10)

def show_contact_profile_page(contact_user_id):
    
    try:
        # Check if the current user is blocked by the contact
        cursor.execute("""
            SELECT status FROM contacts 
            WHERE user_id = %s AND contact_user_id = %s
        """, (contact_user_id, current_user_id))

        block_status = cursor.fetchone()
        
        if block_status and block_status[0] == 'blocked':
            # Fetch only the contact name and created_at for blocked users
            cursor.execute("""
                SELECT contact_name, created_at, email 
                FROM contacts C 
                JOIN users U ON U.user_id = C.contact_user_id  
                WHERE C.user_id = %s AND C.contact_user_id = %s
            """, (current_user_id, contact_user_id))
            
            result = cursor.fetchone()
            if result:
                contact_name, created_at , email = result
                created_at = format_timestamp(created_at)
            else:
                contact_name = "Unknown"
                created_at = "N/A"

            username = "EchoChat User"
            profile_picture_path = None
            last_seen = "Long time ago"
        else:
            # Fetch the full contact profile details
            cursor.execute("""
                SELECT contact_name, username, profile_picture, created_at, last_seen, email 
                FROM contacts C 
                JOIN users U ON U.user_id = C.contact_user_id 
                WHERE C.user_id = %s AND C.contact_user_id = %s
            """, (current_user_id, contact_user_id))

            result = cursor.fetchone()
            
            if result:
                contact_name, username, profile_picture_path, created_at, last_seen, email = result
                created_at = format_timestamp(created_at)
                last_seen = format_timestamp(last_seen)
            else:
                contact_name = "Unknown"
                profile_picture_path = None
                email = "N/A"
                username = "N/A"
                created_at = "N/A"
                last_seen = "N/A"

        canvas_contact.delete("contact_details")
        
        # Display the contact details on the canvas
        canvas_contact.create_text(450, 240, text=f"Contact Name: {contact_name}", anchor="w", font=("futura", 20, "bold"), fill="midnightblue", tags="contact_details")
        canvas_contact.create_text(450, 300, text=f"Username: {username}", anchor="w", font=("futura", 20, "bold"), fill="midnightblue", tags="contact_details")
        canvas_contact.create_text(450, 360, text=f"Email: {email}", anchor="w", font=("futura", 20, "bold"), fill="midnightblue", tags="contact_details")
        canvas_contact.create_text(450, 420, text=f"Joined EchoChat on: {created_at}", anchor="w", font=("futura", 20, "bold"), fill="midnightblue", tags="contact_details")
        canvas_contact.create_text(450, 480, text=f"Last Seen on: {last_seen}", anchor="w", font=("futura", 20, "bold"), fill="midnightblue", tags="contact_details")

        # Display the profile picture if available and not blocked
        if profile_picture_path and os.path.exists(profile_picture_path) and not (block_status and block_status[0] == 'blocked'):
            try:
                img = Image.open(profile_picture_path)
                img = img.resize((250, 250), Image.LANCZOS)
                img = circular_image(img)
                img_tk = ImageTk.PhotoImage(img)

                canvas_contact.create_image(40, 240, anchor='nw', image=img_tk, tags="contact_details")
                canvas_contact.image = img_tk
            except Exception as e:
                messagebox.showerror("Error", f"Error loading profile image: {e}")
        else:
            # Load and display the default profile image
            default_img = Image.open('C:/Users/user/OneDrive/Desktop/messenger/images/user.png')
            default_img = default_img.resize((250, 250), Image.LANCZOS)
            default_img = circular_image(default_img)
            default_img_tk = ImageTk.PhotoImage(default_img)

            canvas_contact.create_image(40, 240, anchor='nw', image=default_img_tk, tags="contact_details")
            canvas_contact.image = default_img_tk

        # Add a button to change the contact name
        change_name_button = tk.Button(contacts_profile_frame, background="mediumpurple1", image=edit_image, command=lambda: change_contact_name(contact_user_id))
        canvas_contact.create_window(410, 240, anchor="w", window=change_name_button, tags="contact_details")

        # Add footer text
        canvas_contact.create_text(1190, 740, text="© 2024 Divyanshu", anchor="se", font=("futura", 10, "bold"), fill="midnightblue")

        # Show the contact profile frame
        show_frame(contacts_profile_frame)
        
    except Exception as e:
        connection.rollback()
        print("Error", f"An error occurred: {e}")
    finally:
        connection.commit()

def format_date(timestamp):
    """Format the timestamp to match WhatsApp style."""
    now = datetime.now()
    date_diff = now - timestamp

    # If the message is today
    if date_diff.days == 0:
        return "Today"

    # If the message was yesterday
    elif date_diff.days == 1:
        return "Yesterday"

    # For specific dates
    else:
        return timestamp.strftime("%b %d, %Y")
    
def load_chat_history(messages_text, contact_user_id):
    global image_refs
    messages_text.config(state=tk.NORMAL)  # Enable editing

    # Clear existing content
    messages_text.delete("1.0", tk.END)

    try:
        cursor.execute("""
            SELECT M.sender_id, M.contents, M.time_stamp, A.file_path 
            FROM messages M 
            LEFT JOIN attachments A ON M.message_id = A.message_id 
            WHERE (M.sender_id = %s AND M.receiver_id = %s) 
            OR (M.sender_id = %s AND M.receiver_id = %s) 
            ORDER BY M.time_stamp
        """, (current_user_id, contact_user_id, contact_user_id, current_user_id))
        
        messages = cursor.fetchall()
        image_refs = []  # Clear previous image references to avoid garbage collection

        previous_date = None  # Store previous message's date to avoid repetition of dates

        for msg in messages:
            sender_id, content, timestamp, file_path = msg
            timestamp_str = timestamp.strftime("%H:%M")
            formatted_date = format_date(timestamp)

            # Show the date only if it's different from the previous message's date
            if previous_date != formatted_date:
                messages_text.insert(tk.END, f"{formatted_date}\n", 'date')
                previous_date = formatted_date

            # Align messages based on the sender
            if sender_id == current_user_id:
                msg_tag = 'sent'
                img_tag = 'sent_img'
                align = 'right'
            else:
                msg_tag = 'received'
                img_tag = 'received_img'
                align = 'left'

            # Add text messages
            if content:
                messages_text.insert(tk.END, f"{content}\t", msg_tag)
                messages_text.insert(tk.END, f"{timestamp_str}\n\n", 'timestamp')  

            # Add image attachments
            if file_path:
                file_extension = os.path.splitext(file_path)[-1].lower()
                if file_extension in ['.jpg', '.jpeg', '.png']:
                    try:
                        img = Image.open(file_path)
                        max_width = 200
                        img.thumbnail((max_width, max_width), Image.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)
                        image_refs.append(img_tk) 

                        if align == 'right':
                            messages_text.insert(tk.END, f"{' ' * 10}", img_tag)
                            messages_text.image_create(tk.END, image=img_tk)
                            messages_text.insert(tk.END, f"\t{timestamp_str}\n\n", 'timestamp')  
                        else:
                            messages_text.insert(tk.END, '\n') 
                            messages_text.image_create(tk.END, image=img_tk)
                            messages_text.insert(tk.END, f"\t{timestamp_str}\n\n", 'timestamp') 

                    except Exception as e:
                        print(f"Error loading image: {e}")
                        messages_text.insert(tk.END, f"Error loading image: {file_path}\n", msg_tag)
                else:
                    # Non-image file attachment
                    messages_text.insert(tk.END, f"File attached: {os.path.basename(file_path)}\n", msg_tag)
                    messages_text.insert(tk.END, f"{timestamp_str}\n\n", 'timestamp')

        # Configure text tags
        messages_text.tag_configure('sent', justify='right', foreground='midnightblue', font=('Arial', 12), wrap='word')
        messages_text.tag_configure('received', justify='left', foreground='midnightblue', font=('Arial', 12), wrap='word')
        messages_text.tag_configure('timestamp', foreground='gray', font=('Arial', 8))
        messages_text.tag_configure('sent_img', justify='right')
        messages_text.tag_configure('received_img', justify='left')
        messages_text.tag_configure('date', justify='center', foreground='black', font=('Arial', 10, 'bold', 'italic'))  # Modified

        # Add margins
        messages_text.tag_add('all', '1.0', 'end')
        messages_text.tag_config('all', lmargin1=10, lmargin2=10, rmargin=38)

        # Disable editing and scroll to the bottom
        messages_text.config(state=tk.DISABLED)
        messages_text.yview(tk.END)

        # Mark unread messages as read
        cursor.execute("""
            UPDATE messages
            SET read = TRUE
            WHERE sender_id = %s AND receiver_id = %s
            AND read = FALSE
        """, (contact_user_id, current_user_id))
        connection.commit()

    except Exception as e:
        print(f"An error occurred while loading chat history: {e}")
        connection.rollback()

def add_contact():
    email = entry_add_email_contact.get()
    contact_name = entry_add_name_contact.get()

    if email:
        cursor.execute("SELECT user_id, username FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result:
            contact_user_id = result[0]
            username = result[1]

            # If no contact name is provided, use the username
            if not contact_name:
                contact_name = username

            cursor.execute(
                "INSERT INTO contacts (user_id, contact_user_id, contact_name) VALUES (%s, %s, %s)",
                (current_user_id, contact_user_id, contact_name)
            )
            connection.commit()

            messagebox.showinfo("Successful", "Contact Added Successfully !!")
            entry_add_name_contact.delete(0, tk.END)
            entry_add_email_contact.delete(0, tk.END)
            show_frame(home_frame)
            load_contacts()
        else:
            messagebox.showerror("Error", f"{email} is not on EchoChat !!")

# signup page

def update_profile_photo():
    global profile_pic_path, current_user_id

    # Open file dialog to select an image
    file_types = [("Image Files", "*.jpg *.jpeg *.png")]
    selected_image = filedialog.askopenfilename(filetypes=file_types)

    if selected_image:
        # If an image is selected, update the profile picture path
        profile_pic_path = selected_image
    else:
        # If no image is selected, use a default image
        profile_pic_path = 'C:/Users/user/OneDrive/Desktop/messenger/images/user.png'  # Update with the correct path to your default image

    try:
        # Update the user's profile picture in the database
        cursor.execute("UPDATE users SET profile_picture = %s WHERE user_id = %s", 
                       (profile_pic_path, current_user_id))
        connection.commit()

        # Optionally, you can update the profile picture on the navbar immediately after updating
        update_navbar_profile_picture()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while updating the profile photo: {e}")

signup_frame = tk.Frame(container)

canvas_signup = tk.Canvas(signup_frame)
canvas_signup.place(relx=0, rely=0, relwidth=1, relheight=1)

canvas_signup.create_image(0, 0, anchor="nw", image=back_image_app)

canvas_signup.create_image(600,445, anchor="center", image=background_image)

canvas_signup.create_image(600,70, anchor="center", image=logo_image)

canvas_signup.create_text(600, 150, text="CREATE YOUR ACCOUNT", font=("futura", 30, "bold"), fill="midnightblue")

canvas_signup.create_line(360, 180,839, 180, fill="midnightblue", width=6)

canvas_signup.create_text(100, 270, text="ENTER YOUR EMAIL",anchor="w", font=("futura", 20, "bold"), fill="midnightblue")

email_entry_signup = tk.Entry(signup_frame, font=("futura", 18,"bold"),fg="midnightblue",border=5,width=30,background="lavender")

canvas_signup.create_window(450,270,anchor="w", window=email_entry_signup)

canvas_signup.create_text(100, 350, text="ENTER YOUR NAME",anchor="w", font=("futura", 20, "bold"), fill="midnightblue")

uname_entry_signup = tk.Entry(signup_frame, font=("futura", 18,"bold"),fg="midnightblue",border=5,width=30,background="lavender")

canvas_signup.create_window(450,350,anchor="w", window=uname_entry_signup)

canvas_signup.create_text(67, 430, text="ENTER YOUR PASSWORD",anchor="w", font=("futura", 20, "bold"), fill="midnightblue")

password_entry_signup = tk.Entry(signup_frame,show="*", font=("futura", 18,"bold"),fg="midnightblue",border=5,width=30,background="lavender")

canvas_signup.create_window(450,430,anchor="w", window=password_entry_signup)

canvas_signup.create_text(120, 510, text="ENTER PROFILE",anchor="w", font=("futura", 20, "bold"), fill="midnightblue")

button = tk.Button(signup_frame,text="SELECT IMAGE", border=5, bg="lavender",font=("futura",15,"bold") , fg="midnightblue" , width=15, command=update_profile_photo)
button_window =canvas_signup.create_window(650,510, anchor="center", window=button)

registered_already_text=canvas_signup.create_text(650, 570, text="Already Registered ??",anchor="center", font=("futura", 14, "bold","underline"), fill="blue")
canvas_signup.tag_bind(registered_already_text, "<Button-1>",lambda event: show_frame(login_frame))

button = tk.Button(signup_frame,text="REGISTER", border=5, bg="lavender",font=("futura",17,"bold") ,pady=5, fg="midnightblue" , width=15, command=register_user)
button_window =canvas_signup.create_window(650,640, anchor="center", window=button)

canvas_signup.create_text(1190, 740, text="© 2024 Divyanshu",anchor="se", font=("futura", 10, "bold"), fill="midnightblue")

signup_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# login page 

login_frame = tk.Frame(container)

canvas_login = tk.Canvas(login_frame)
canvas_login.place(relx=0, rely=0, relwidth=1, relheight=1)

canvas_login.create_image(0, 0, anchor="nw", image=back_image_app)

canvas_login.create_image(600,445, anchor="center", image=background_image)

canvas_login.create_image(600,70, anchor="center", image=logo_image)

canvas_login.create_text(600, 150, text="LOGIN TO YOUR ACCOUNT", font=("futura", 30, "bold"), fill="midnightblue")

canvas_login.create_line(351, 180,850, 180, fill="midnightblue", width=6)

canvas_login.create_text(100, 340, text="ENTER YOUR EMAIL",anchor="w", font=("futura", 20, "bold"), fill="midnightblue")

email_entry_login = tk.Entry(login_frame, font=("futura", 18,"bold"),border=5,width=30,fg="midnightblue",background="lavender")

canvas_login.create_window(450,340,anchor="w", window=email_entry_login)

canvas_login.create_text(67, 430, text="ENTER YOUR PASSWORD",anchor="w", font=("futura", 20, "bold"), fill="midnightblue")

password_entry_login = tk.Entry(login_frame,show="*", font=("futura", 18,"bold"),fg="midnightblue",border=5,width=30,background="lavender")

canvas_login.create_window(450,430,anchor="w", window=password_entry_login)

dont_have_acc_text=canvas_login.create_text(650, 500, text="Dont Have account ??",anchor="center", font=("futura", 14, "bold","underline"), fill="blue")
canvas_login.tag_bind(dont_have_acc_text, "<Button-1>",lambda event: show_frame(signup_frame))

button_login = tk.Button(login_frame,text="LOGIN", border=5, bg="lavender",font=("futura",17,"bold") ,pady=5, fg="midnightblue" , width=15, command=login_user)
button_window =canvas_login.create_window(650,580, anchor="center", window=button_login)

canvas_login.create_text(1190, 740, text="© 2024 Divyanshu",anchor="se", font=("futura", 10, "bold"), fill="midnightblue")

login_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# home page 

style = ttk.Style()
style.configure('TScrollbar', gripcount=0,background='darkblue', troughcolor='lightblue',bordercolor='blue',arrowcolor='white')

home_frame = tk.Frame(container)

canvas_home = tk.Canvas(home_frame)
canvas_home.place(relx=0, rely=0, relwidth=1, relheight=1)

canvas_home.create_image(0, 0, anchor="nw", image=back_image_app)

canvas_home.create_image(600, 445, anchor="center", image=background_image)

#(contacts frame) home page 

contacts_canvas = tk.Canvas(home_frame, background="lavender",border=5)
contacts_canvas.place(x=20, y=60, width=350, relheight=0.8)

nav_bar_frame = tk.Frame(home_frame, background="lavender", border=2)
nav_bar_frame.place(x=20, y=698, width=350, height=62, anchor="w")

canvas_nav_bar = tk.Canvas(nav_bar_frame,background="lavender")
canvas_nav_bar.place(x=0,y=0,width=350, height=62, anchor="nw")

button = tk.Button(nav_bar_frame,image=settings_image,border=5, bg="lavender",font=("futura",17,"bold") ,pady=2, fg="midnightblue"  , command=lambda:show_frame(settings_frame))
button_window =canvas_nav_bar.create_window(235,40, anchor="center", window=button)
canvas_nav_bar.create_text(235,10,text="Settings",anchor="center", font=("futura", 10, "bold"), fill="midnightblue")

button = tk.Button(nav_bar_frame,image=help_image,border=5, bg="lavender",font=("futura",17,"bold") ,pady=2, fg="midnightblue"  , command=lambda:show_frame(help_frame))
button_window =canvas_nav_bar.create_window(315,40, anchor="center", window=button)
canvas_nav_bar.create_text(315,10,text="Help",anchor="center", font=("futura", 10, "bold"), fill="midnightblue")

button = tk.Button(nav_bar_frame,image=add_contact_image,border=5, bg="lavender",font=("futura",17,"bold") ,pady=2, fg="midnightblue"  , command= lambda: show_frame(add_contacts_frame))
button_window =canvas_nav_bar.create_window(150,40, anchor="center", window=button)

profile_button = tk.Button(nav_bar_frame, command=open_profile_frame, background="lavender", border=0)
profile_button.pack()

canvas_nav_bar.create_text(140,10,text="Add Contacts",anchor="center", font=("futura", 10, "bold"), fill="midnightblue")

contacts_frame = tk.Frame(contacts_canvas)

contacts_canvas.create_window((0, 0), window=contacts_frame, anchor='nw')
contacts_frame.bind("<Configure>", lambda e: contacts_canvas.configure(scrollregion=contacts_canvas.bbox("all")))

canvas_home.create_text(1190, 747, text="© 2024 Divyanshu",anchor="se", font=("futura", 10, "bold"), fill="midnightblue")

canvas_home.create_text(25,30,anchor="w", text="CONTACTS", font=("futura", 30, "bold"), fill="midnightblue")

# chats Frame (in home page )

chat_canvas= tk.Canvas(home_frame,background="lavender")
chat_canvas.place(x=380, y=120, width=780, relheight=0.75)

chat_name_frame = tk.Frame(home_frame, background="lavender", border=2)
chat_name_frame.place(x=380, y=40, width=797, height=80, anchor="nw")

scrollbar_chat = ttk.Scrollbar(home_frame, orient="vertical", command=contacts_canvas.yview, style='TScrollbar')
scrollbar_chat.place(x=1177, y=120, relheight=0.75, anchor="ne")
chat_canvas.configure(yscrollcommand=scrollbar_chat.set)

chat_frame= tk.Frame(chat_canvas)
chat_canvas.create_window((0, 0), window=chat_frame, anchor='nw')
chat_frame.bind("<Configure>", lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all")))

placeholder_text = "Type a message ..."
text_entry_chat = tk.Entry(home_frame, font=("futura", 15, "bold"), border=5, width=63, background="lavender")
text_entry_chat.place(x=1090, y=710, anchor="e")

add_placeholder(text_entry_chat, "Type a message")

text_entry_chat.bind("<FocusIn>", lambda event: remove_placeholder(event, "Type a message"))
text_entry_chat.bind("<FocusOut>", lambda event: restore_placeholder(event, "Type a message"))

canvas_home.create_window(1090,710,anchor="e", window=text_entry_chat)

button = tk.Button(home_frame,image=forward_image,border=5, bg="lavender",font=("futura",17,"bold") ,pady=2, fg="midnightblue"  , command=lambda: send_message(text_entry_chat.get(), messages_text))
button_window =canvas_home.create_window(1160,710, anchor="center", window=button)

button = tk.Button(home_frame,image=attach_image,border=5, bg="lavender",font=("futura",17,"bold") ,pady=2, fg="midnightblue"  , command=attach_file)
button_window =canvas_home.create_window(1115,710, anchor="center", window=button)

home_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

#contacts page (profile of contact )

contacts_profile_frame = tk.Frame(container)

canvas_contact = tk.Canvas(contacts_profile_frame)
canvas_contact.place(relx=0, rely=0, relwidth=1, relheight=1)

canvas_contact.create_image(0, 0, anchor="nw", image=back_image_app)
canvas_contact.create_image(600,445, anchor="center", image=background_image)

button_back_contact = tk.Button(contacts_profile_frame, text="BACK", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=10, command=lambda: show_frame(home_frame))
canvas_contact.create_window(150, 100, anchor="center", window=button_back_contact)

canvas_contact.create_image(600,70, anchor="center", image=logo_image)

contacts_profile_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# add contact frame

def cancel_add_contact():
    show_frame(home_frame)
    entry_add_email_contact.delete(0,tk.END)
    entry_add_name_contact.delete(0,tk.END)

add_contacts_frame = tk.Frame(container)

canvas_add_contact = tk.Canvas(add_contacts_frame)
canvas_add_contact.place(relx=0, rely=0, relwidth=1, relheight=1)

canvas_add_contact.create_image(0, 0, anchor="nw", image=back_image_app)

canvas_add_contact.create_image(600,445, anchor="center", image=background_image)

canvas_add_contact.create_image(600,70, anchor="center", image=logo_image)

canvas_add_contact.create_text(600, 150, text="ADD CONTACT", font=("futura", 30, "bold"), fill="midnightblue")

canvas_add_contact.create_line(360, 180,839, 180, fill="midnightblue", width=6)

canvas_add_contact.create_text(70, 270, text="ENTER CONTACT EMAIL",anchor="w", font=("futura", 20, "bold"), fill="midnightblue")

entry_add_email_contact = tk.Entry(add_contacts_frame, font=("futura", 18,"bold"),border=5,width=30,background="lavender")

canvas_add_contact.create_window(500,270,anchor="w", window=entry_add_email_contact)

canvas_add_contact.create_text(70, 400, text="ENTER CONTACT NAME",anchor="w", font=("futura", 20, "bold"), fill="midnightblue")

entry_add_name_contact = tk.Entry(add_contacts_frame, font=("futura", 18,"bold"),border=5,width=30,background="lavender")

canvas_add_contact.create_window(500,400,anchor="w", window=entry_add_name_contact )

button_contact_add = tk.Button(add_contacts_frame,text="ADD CONTACT", border=5, bg="lavender",font=("futura",17,"bold") ,pady=5, fg="midnightblue" , width=15, command=add_contact)
button_window =canvas_add_contact.create_window(500,550, anchor="center", window=button_contact_add)

button_cancel_add = tk.Button(add_contacts_frame,text="CANCEL", border=5, bg="lavender",font=("futura",17,"bold") ,pady=5, fg="midnightblue" , width=15, command=cancel_add_contact)
button_window =canvas_add_contact.create_window(800,550, anchor="center", window=button_cancel_add )

canvas_add_contact.create_text(1190, 740, text="© 2024 Divyanshu",anchor="se", font=("futura", 10, "bold"), fill="midnightblue")

add_contacts_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# profile page

def change_username_profile():
    change_name_frame = tk.Toplevel(background="lavender")
    change_name_frame.title("Change Username")
    change_name_frame.iconbitmap("images/icon.ico")

    tk.Label(change_name_frame, text=" New Username ", fg="midnightblue", bg="lavender", font=("futura", 20, "bold")).pack(pady=10)
    entry_new_name = tk.Entry(change_name_frame, bg="lavender", fg="midnightblue", border=5, font=("futura", 15), width=20)
    entry_new_name.pack(pady=10, padx=10)

    def on_change_click():
        new_username = entry_new_name.get()
        if new_username:
            update_username(current_user_id, new_username)
            change_name_frame.destroy()
            open_profile_frame()
        else:
            messagebox.showerror("Error", "Username cannot be empty.")

    tk.Button(change_name_frame, border=5, text="CHANGE", font=("futura", 16, "bold"), bg="lavender", fg="midnightblue", command=on_change_click).pack(pady=10)

def update_username(user_id, new_username):
    try:
        cursor.execute("UPDATE users SET username = %s WHERE user_id = %s", (new_username, user_id))
        connection.commit()
        messagebox.showinfo("Success", "Username updated successfully.")
    except Exception as e:
        print(f"Exception occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def open_profile_frame():
    global current_user_id
    try:
        cursor.execute("SELECT username, email, last_seen, created_at, profile_picture FROM users WHERE user_id = %s", (current_user_id,))
        user_details = cursor.fetchone()

        if user_details:
            name, email, last_seen, created_at, profile_picture_path = user_details
            created_at = format_timestamp(created_at)
            last_seen = format_timestamp(last_seen)

            for widget in profile_frame.winfo_children():
                widget.destroy()

            canvas_profile = tk.Canvas(profile_frame)
            canvas_profile.place(relx=0, rely=0, relwidth=1, relheight=1)
            canvas_profile.create_image(0, 0, anchor="nw", image=back_image_app)
            canvas_profile.create_image(600,445, anchor="center", image=background_image)
            canvas_profile.create_image(600, 70, anchor="center", image=logo_image)
            
            button_back_profile = tk.Button(profile_frame, text="BACK", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=10, command=lambda: show_frame(home_frame))
            canvas_profile.create_window(150, 100, anchor="center", window=button_back_profile)

            button_logout_profile = tk.Button(profile_frame, text="LOG OUT", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=10, command=logout)
            canvas_profile.create_window(1130, 100, anchor="e", window=button_logout_profile )

            if profile_picture_path:
                img = Image.open(profile_picture_path)
                img = img.resize((250, 250), Image.LANCZOS)
                img = circular_image(img)
                img_tk = ImageTk.PhotoImage(img)
                image_refs.append(img_tk)  
                canvas_profile.create_image(50, 230, anchor='nw', image=img_tk)

            canvas_profile.create_text(400, 270, anchor="w", text=f"Name: {name}", font=("futura", 20, "bold"), fill="midnightblue")
            canvas_profile.create_text(400, 330, anchor="w", text=f"Email: {email}", font=("futura", 20, "bold"), fill="midnightblue")
            canvas_profile.create_text(400, 390, anchor="w", text=f"Last Seen on: {last_seen}", font=("futura", 20, "bold"), fill="midnightblue")
            canvas_profile.create_text(400, 450, anchor="w", text=f"Joined EchoChat on: {created_at}", font=("futura", 20, "bold"), fill="midnightblue")

            button_change_picture = tk.Button(profile_frame, text="Change Profile", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=15, command=change_profile_picture)
            canvas_profile.create_window(68, 520, anchor="w", window=button_change_picture)

            button_delete_picture = tk.Button(profile_frame, text="Remove Profile", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=15, command=delete_profile_picture)
            canvas_profile.create_window(68, 580, anchor="w", window=button_delete_picture)

            button_change_username = tk.Button(profile_frame, background="mediumpurple1",image=edit_image, command=change_username_profile)
            canvas_profile.create_window(360, 270, anchor="w", window=button_change_username)

            canvas_profile.create_text(1190, 740, text="© 2024 Divyanshu",anchor="se", font=("futura", 10, "bold"), fill="midnightblue")

            profile_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            show_frame(profile_frame)
        else:
            messagebox.showerror("Error", "User details not found.")
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def logout():
    show_frame(login_frame)
    email_entry_login.delete(0,tk.END)
    password_entry_login.delete(0,tk.END)
    email_entry_signup.delete(0,tk.END)
    password_entry_signup.delete(0,tk.END)
    uname_entry_signup.delete(0,tk.END)

def change_profile_picture():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        try:
            cursor.execute("UPDATE users SET profile_picture = %s WHERE user_id = %s", (file_path, current_user_id))
            connection.commit()
            messagebox.showinfo("Success", "Profile picture updated successfully.")
            open_profile_frame() 
        except Exception as e:
            print(f"Exception occurred: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

def delete_profile_picture():
    try:
        default_image_path = 'C:/Users/user/OneDrive/Desktop/messenger/images/user.png'
        
        cursor.execute("UPDATE users SET profile_picture = %s WHERE user_id = %s", (default_image_path, current_user_id))
        connection.commit()
        
        messagebox.showinfo("Success", "Profile picture reset to default successfully.")
        open_profile_frame() 
    except Exception as e:
        print(f"Exception occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

# settings page  

def load_block_contacts():
    clear_contact_list()
    global block_contact_images
    block_contacts_canvas.delete("all")
    
    cursor.execute(" SELECT U.user_id, C.contact_name, U.profile_picture  FROM contacts C  JOIN users U ON U.user_id = C.contact_user_id WHERE C.user_id = %s and status = 'unblocked' ORDER BY C.contact_name ASC ", (current_user_id,))

    contacts = cursor.fetchall()
    y = 10  
    default_image_path = 'C:/Users/user/OneDrive/Desktop/messenger/images/user.png'

    for contact in contacts:
        contact_user_id = contact[0]
        contact_name = contact[1]
        profile_picture_path = contact[2] if contact[2] else default_image_path

        if profile_picture_path and os.path.exists(profile_picture_path):
            try:
                img = Image.open(profile_picture_path)
                img = img.resize((50, 50), Image.LANCZOS)
                img = circular_image(img)  
                img_tk_block = ImageTk.PhotoImage(img)

                block_contacts_canvas.create_image(35, y + 25, image=img_tk_block, anchor="center")
                block_contact_images.append(img_tk_block)  
                
            except Exception as e:
                messagebox.showerror("Error", f"Error loading image: {e}")
        else:
            messagebox.showerror("Error", f"Profile picture not found at {profile_picture_path}")

        contact_name_id = block_contacts_canvas.create_text(90, y + 25, text=contact_name, anchor="w", font=("Arial", 12))

        block_contacts_canvas.tag_bind(contact_name_id, "<Button-1>", lambda e, user_id=contact_user_id: block_contact(user_id))

        y += 60  

    block_contacts_canvas.update_idletasks()  
    block_contacts_canvas.config(scrollregion=block_contacts_canvas.bbox("all"))  

def load_unblock_contacts():
    clear_contact_list()
    global unblock_contact_images
    unblock_contacts_canvas.delete("all")
    
    cursor.execute(" SELECT U.user_id, C.contact_name, U.profile_picture  FROM contacts C  JOIN users U ON U.user_id = C.contact_user_id WHERE C.user_id = %s and status = 'blocked' ORDER BY C.contact_name ASC ", (current_user_id,))

    contacts = cursor.fetchall()
    y = 10  
    default_image_path = 'C:/Users/user/OneDrive/Desktop/messenger/images/user.png'

    for contact in contacts:
        contact_user_id = contact[0]
        contact_name = contact[1]
        profile_picture_path = contact[2] if contact[2] else default_image_path

        if profile_picture_path and os.path.exists(profile_picture_path):
            try:
                img = Image.open(profile_picture_path)
                img = img.resize((50, 50), Image.LANCZOS)
                img = circular_image(img) 
                img_tk_unblock = ImageTk.PhotoImage(img)

                unblock_contacts_canvas.create_image(35, y + 25, image=img_tk_unblock , anchor="center")
                unblock_contact_images.append(img_tk_unblock ) 
                
            except Exception as e:
                messagebox.showerror("Error", f"Error loading image: {e}")
        else:
            messagebox.showerror("Error", f"Profile picture not found at {profile_picture_path}")

        contact_name_id = unblock_contacts_canvas.create_text(90, y + 25, text=contact_name, anchor="w", font=("Arial", 12))

        unblock_contacts_canvas.tag_bind(contact_name_id, "<Button-1>", lambda e, user_id=contact_user_id: unblock_contact(user_id))

        y += 60  

    unblock_contacts_canvas.update_idletasks()  
    unblock_contacts_canvas.config(scrollregion=unblock_contacts_canvas.bbox("all"))  

def unblock_contact(user_id):
    try:
        cursor.execute("UPDATE contacts SET status = 'unblocked' WHERE user_id = %s AND contact_user_id = %s", (current_user_id, user_id))
        connection.commit()
        messagebox.showinfo("Contact Unblocked", "The contact has been unblocked successfully.")
        load_unblock_contacts()  
        load_contacts()
    except Exception as e:
        messagebox.showerror("Error", f"Error unblocking contact: {e}")

def block_contact(user_id):
    try:
        cursor.execute("UPDATE contacts SET status = 'blocked' WHERE user_id = %s AND contact_user_id = %s", (current_user_id, user_id))
        connection.commit()
        messagebox.showinfo("Contact Blocked", "The contact has been blocked successfully.")
        load_block_contacts()
        load_contacts()  
    except Exception as e:
        messagebox.showerror("Error", f"Error blocking contact: {e}")

def open_block_contact():
    load_block_contacts()
    load_unblock_contacts()
    load_contacts()

def clear_contact_list():
    global  block_contact_images
    
    block_contacts_canvas.delete("all")
    unblock_contacts_canvas.delete("all")
    
    block_contact_images.clear()
    unblock_contact_images.clear()

    block_contacts_canvas.config(scrollregion=(0, 0, 0, 0))

def back_settings_page():
    clear_contact_list()
    show_frame(home_frame)

settings_frame= tk.Frame(container)

canvas_settings = tk.Canvas(settings_frame)
canvas_settings .place(relx=0, rely=0, relwidth=1, relheight=1)

canvas_settings .create_image(0, 0, anchor="nw", image=back_image_app)

canvas_settings .create_image(600,445, anchor="center", image=background_image)

canvas_settings .create_image(600,70, anchor="center", image=logo_image)

canvas_settings.create_text(600, 130, text="SETTINGS",anchor="center", font=("futura", 30, "bold"), fill="midnightblue")

button_cancel_settings = tk.Button(settings_frame, text="BACK", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=10, command=back_settings_page)
canvas_settings.create_window(150, 100, anchor="center", window=button_cancel_settings)

button_profile_settings = tk.Button(settings_frame, text="PROFILE", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=10, command=open_profile_frame)
canvas_settings.create_window(1130, 100, anchor="e", window=button_profile_settings)

button_block_settings = tk.Button(settings_frame, text="BLOCK CONTACT", border=5,width=20, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", command=load_block_contacts)
canvas_settings.create_window(380, 190, anchor="center", window=button_block_settings )

button_unblock_settings = tk.Button(settings_frame, text="UNBLOCK CONTACT", border=5,width=20, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", command=load_unblock_contacts)
canvas_settings.create_window(820, 190, anchor="center", window=button_unblock_settings )

block_contact_frame= tk.Frame(settings_frame)
canvas_settings.create_text(375, 250, text="Contacts",anchor="center", font=("futura", 20, "bold"), fill="midnightblue")
canvas_settings.create_text(815, 250, text="Blocked Contacts",anchor="center", font=("futura", 20, "bold"), fill="midnightblue")

block_contacts_canvas= tk.Canvas(settings_frame, background="lavender",border=5)
block_contacts_canvas.place(x=230, y=270, width=300, relheight=0.6)

block_contacts_canvas.create_window((0, 0), window=block_contact_frame, anchor='nw')
block_contact_frame.bind("<Configure>", lambda e: block_contacts_canvas.configure(scrollregion=block_contacts_canvas.bbox("all")))

unblock_contact_frame= tk.Frame(settings_frame)

unblock_contacts_canvas= tk.Canvas(settings_frame, background="lavender",border=5)
unblock_contacts_canvas.place(x=670, y=270, width=300, relheight=0.6)

unblock_contacts_canvas.create_window((0, 0), window=unblock_contact_frame, anchor='nw')
unblock_contact_frame.bind("<Configure>", lambda e: unblock_contacts_canvas.configure(scrollregion=unblock_contacts_canvas.bbox("all")))

canvas_settings.create_text(1190, 740, text="© 2024 Divyanshu",anchor="se", font=("futura", 10, "bold"), fill="midnightblue")

settings_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# Help page  

def open_github():
    webbrowser.open("https://github.com/divyanshu2580")

def open_instagram():
    webbrowser.open("https://www.instagram.com/droan_sharma_26/")

def open_linkedin():
    webbrowser.open("https://www.linkedin.com/in/divyanshu-sharma-778282240/")

def open_gmail():
    webbrowser.open("mailto:droansharma7296@gmail.com")

help_frame= tk.Frame(container)

canvas_help = tk.Canvas(help_frame)
canvas_help .place(relx=0, rely=0, relwidth=1, relheight=1)

canvas_help.create_image(0, 0, anchor="nw", image=back_image_app)

canvas_help.create_image(600,445, anchor="center", image=background_image)

canvas_help.create_image(600,70, anchor="center", image=logo_image)

button_cancel_help = tk.Button(help_frame, text="BACK", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=10, command=lambda: show_frame(home_frame))
canvas_help.create_window(150, 100, anchor="center", window=button_cancel_help)

button_profile_help = tk.Button(help_frame, text="PROFILE", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=10, command=open_profile_frame)
canvas_help.create_window(1130, 100, anchor="e", window=button_profile_help)

canvas_help.create_text(100, 200, text="ECHO CHAT",anchor="w" , font=("futura", 30, "bold"), fill="midnightblue")

canvas_help.create_line(50, 160,1150, 160, fill="midnightblue", width=4)

canvas_help.create_text(200, 250, text="Made by © 2024 Divyanshu Sharma", anchor="w",font=("futura", 20, "bold"), fill="midnightblue")

canvas_help.create_line(50, 290,1150, 290, fill="midnightblue", width=4)

canvas_help.create_text(100, 330, text="CONTACT US",anchor="w" , font=("futura", 30, "bold"), fill="midnightblue")

button_gmail_help = tk.Button(help_frame, text="GMAIL", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=11, command=open_gmail)
canvas_help.create_window(200, 400, anchor="w", window=button_gmail_help)

button_instagram_help = tk.Button(help_frame, text="INSTAGRAM", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=11, command=open_instagram)
canvas_help.create_window(400, 400, anchor="w", window=button_instagram_help )

button_linkedin_help = tk.Button(help_frame, text="LINKEDIN", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=11, command=open_linkedin)
canvas_help.create_window(600, 400, anchor="w", window=button_linkedin_help )

button_github_help = tk.Button(help_frame, text="GITHUB", border=5, bg="lavender", font=("futura", 17, "bold"), pady=5, fg="midnightblue", width=11, command=open_github)
canvas_help.create_window(800, 400, anchor="w", window=button_github_help )

canvas_help.create_line(50, 460,1150, 460, fill="midnightblue", width=4)

canvas_help.create_text(100, 500, text="ABOUT US",anchor="w" ,font=("futura", 30, "bold"), fill="midnightblue")

canvas_help.create_text(200, 600, text="Divyanshu Sharma \nDept. of Science and Technology \nJain University, Bangalore\n@ 2024 Made project under the guidance of Ms. Shaikh Dilchashmi ",anchor="w" ,font=("futura", 20, "bold"), fill="midnightblue")

canvas_help.create_line(50, 685, 1150 , 685, fill="midnightblue", width=4)

canvas_help.create_text(1190, 740, text="© 2024 Divyanshu",anchor="se", font=("futura", 10, "bold"), fill="midnightblue")

help_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


root.protocol("WM_DELETE_WINDOW", on_closing)
load_contacts()
show_frame(login_frame)
root.mainloop()
