import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3
import hashlib
import uuid
import pyttsx3
import threading

load_dotenv()

# Database setup
def initialize_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

# Password hashing functions
def hash_password(password, salt=None):
    if salt is None:
        salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512((password + salt).encode('utf-8')).hexdigest()
    return hashed_password, salt

def verify_password(stored_hash, stored_salt, provided_password):
    new_hash, _ = hash_password(provided_password, stored_salt)
    return new_hash == stored_hash

class LoginPage:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("Login / Sign Up")
        self.root.geometry("500x400")
        self.on_login_success = on_login_success
        
        # Create notebook for login/signup tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Login tab
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")
        self.setup_login_tab()
        
        # Signup tab
        self.signup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.signup_frame, text="Sign Up")
        self.setup_signup_tab()
    
    def setup_login_tab(self):
        # Login tab content
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.login_username = ttk.Entry(self.login_frame)
        self.login_username.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.login_password = ttk.Entry(self.login_frame, show="*")
        self.login_password.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        self.login_btn = ttk.Button(self.login_frame, text="Login", command=self.attempt_login)
        self.login_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Bind Enter key to login attempt
        self.login_password.bind("<Return>", lambda event: self.attempt_login())
        
        # Configure grid weights
        self.login_frame.columnconfigure(1, weight=1)
    
    def setup_signup_tab(self):
        # Signup tab content
        ttk.Label(self.signup_frame, text="Choose Username:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.signup_username = ttk.Entry(self.signup_frame)
        self.signup_username.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(self.signup_frame, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.signup_password = ttk.Entry(self.signup_frame, show="*")
        self.signup_password.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(self.signup_frame, text="Confirm Password:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.signup_confirm_password = ttk.Entry(self.signup_frame, show="*")
        self.signup_confirm_password.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        self.signup_btn = ttk.Button(self.signup_frame, text="Create Account", command=self.attempt_signup)
        self.signup_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Bind Enter key to signup attempt
        self.signup_confirm_password.bind("<Return>", lambda event: self.attempt_signup())
        
        # Configure grid weights
        self.signup_frame.columnconfigure(1, weight=1)
    
    def attempt_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, password_hash, salt FROM users WHERE username=?", (username,))
            result = cursor.fetchone()
            
            if result:
                user_id, stored_hash, salt = result
                if verify_password(stored_hash, salt, password):
                    self.on_login_success(username, user_id)
                else:
                    messagebox.showerror("Error", "Invalid username or password")
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()
    
    def attempt_signup(self):
        username = self.signup_username.get().strip()
        password = self.signup_password.get().strip()
        confirm_password = self.signup_confirm_password.get().strip()
        
        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords don't match")
            return
            
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
            
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        try:
            # Check if username already exists
            cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return
            
            # Hash password and store user
            password_hash, salt = hash_password(password)
            user_id = uuid.uuid4().hex
            cursor.execute(
                "INSERT INTO users (id, username, password_hash, salt) VALUES (?, ?, ?, ?)",
                (user_id, username, password_hash, salt)
            )
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully! You can now login.")
            self.notebook.select(0)  # Switch to login tab
            self.login_username.delete(0, tk.END)
            self.login_username.insert(0, username)
            self.login_password.focus()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

class ChatBotGUI:
    def __init__(self, root, username, user_id):
        self.user_id = user_id
        self.username = username
        self.root = root
        self.root.title(f"AI ChatBot Assistant - Welcome {username}")
        self.root.geometry("600x500")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Add logout button
        self.logout_btn = tk.Button(
            root,
            text="Logout",
            command=self.logout,
            font=('Arial', 10),
            bg='#f44336',
            fg='white'
        )
        self.logout_btn.place(relx=0.95, rely=0.02, anchor=tk.NE)
        
        # Create chat display area
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.chat_display.pack(pady=(40, 10), padx=10, fill=tk.BOTH, expand=True)
        
        # Create input area
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # User input field
        self.user_input = tk.Entry(self.input_frame, font=('Arial', 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.send_message)
        
        # Send button
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Add initial greeting
        greeting = f"Hello {username}, I'm your AI chatbot to help you through your daily activities. How can I assist you today?"
        self.display_message("AI", greeting)
        # self.speak(greeting)

        self.load_chat_history(user_id)

        self.clear_btn = tk.Button(
            root,
            text="Clear History",
            command=self.confirm_clear_history,
            font=('Arial', 10),
            bg='#ff9800',  # Orange color
            fg='white'
        )
        self.clear_btn.place(relx=0.16, rely=0.02, anchor=tk.NE)
    def confirm_clear_history(self):
        # Show confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Clear History",
            "Are you sure you want to delete all chat history?\nThis action cannot be undone.",
            icon='warning'
        )
        if confirm:
            self.clear_chat_history()

    def clear_chat_history(self):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            # Delete all messages for this user
            cursor.execute(
                "DELETE FROM chat_history WHERE user_id = ?",
                (self.user_id,)
            )
            conn.commit()
            
            # Clear the chat display
            self.chat_display.configure(state='normal')
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.configure(state='disabled')
            
            # Show confirmation
            messagebox.showinfo(
                "History Cleared",
                "All chat history has been deleted."
            )
            
            # Re-add the initial greeting
            greeting = f"Hello {self.username}, I'm your AI chatbot. Your chat history has been cleared."
            self.display_message("AI", greeting)
            
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error",
                f"Failed to clear history: {str(e)}"
            )
        finally:
            if conn:
                conn.close()

    def logout(self):
        # Save any pending message
        current_message = self.user_input.get().strip()
        if current_message:
            self.save_message_to_history(self.user_id, "You", current_message)
        
        # Clear the chat interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Return to login page
        AppController(self.root)
    
    def display_message(self, sender, message):
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)
    
    def send_message(self, event=None):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
            
        if user_text.lower() in ["bye", "exit", "quit"]:
            self.display_message("You", user_text)
            goodbye_msg = "Goodbye! Have a great day!"
            self.display_message("AI", goodbye_msg)
            self.speak(goodbye_msg)
            self.user_input.delete(0, tk.END)
            self.root.after(2000, self.root.destroy)
            return
            
        self.display_message("You", user_text)
        self.save_message_to_history(self.user_id, "You", user_text)
        
        try:
            # Get AI response
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_text}]
            )
            ai_response = response.choices[0].message.content.strip()
            self.display_message("AI", ai_response)
            self.save_message_to_history(self.user_id, "AI", ai_response)
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.display_message("AI", error_msg)
            
    def save_message_to_history(self, user_id, sender, message):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)",
            (user_id, sender, message)
        )
        conn.commit()
        conn.close()

    def load_chat_history(self, user_id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT sender, message FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC",
                (user_id,)
            )
            rows = cursor.fetchall()
            for sender, message in rows:
                self.display_message(sender, message)
        except sqlite3.Error as e:
            print(f"Error loading chat history: {e}")
        finally:
            conn.close()
        

class AppController:
    def __init__(self, root):
        self.root = root
        initialize_database()
        self.show_login_page()
    
    def show_login_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create new login page
        self.login_page = LoginPage(self.root, self.on_login_success)
    
    def on_login_success(self, username, user_id):
        # Clear the login page
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show the chatbot interface
        self.chatbot = ChatBotGUI(self.root, username, user_id)


if __name__ == "__main__":
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()