import tkinter as tk
from tkinter import scrolledtext, messagebox
from openai import OpenAI
from dotenv import load_dotenv
import os
from database import save_message_to_history, load_chat_history, clear_chat_history

load_dotenv()

class ChatBotGUI:
    def __init__(self, root, username, user_id):
        self.user_id = user_id
        self.username = username
        self.root = root
        self.root.title(f"AI ChatBot Assistant - Welcome {username}")
        self.root.geometry("600x500")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.setup_ui()
        self.load_chat_history()
    
    def setup_ui(self):
        # Add logout button
        self.logout_btn = tk.Button(
            self.root,
            text="Logout",
            command=self.logout,
            font=('Arial', 10),
            bg='#f44336',
            fg='white'
        )
        self.logout_btn.place(relx=0.95, rely=0.02, anchor=tk.NE)
        
        # Create chat display area
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled')
        self.chat_display.pack(pady=(40, 10), padx=10, fill=tk.BOTH, expand=True)
        
        # Create input area
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # User input field
        self.user_input = tk.Entry(self.input_frame, font=('Arial', 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.send_message)
        
        # Send button
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clear history button
        self.clear_btn = tk.Button(
            self.root,
            text="Clear History",
            command=self.confirm_clear_history,
            font=('Arial', 10),
            bg='#ff9800',
            fg='white'
        )
        self.clear_btn.place(relx=0.16, rely=0.02, anchor=tk.NE)
        
        # Add initial greeting
        greeting = f"Hello {self.username}, I'm your AI chatbot to help you through your daily activities. How can I assist you today?"
        self.display_message("AI", greeting)
    
    def confirm_clear_history(self):
        confirm = messagebox.askyesno(
            "Confirm Clear History",
            "Are you sure you want to delete all chat history?\nThis action cannot be undone.",
            icon='warning'
        )
        if confirm:
            self.clear_chat_history()

    def clear_chat_history(self):
        if clear_chat_history(self.user_id):
            # Clear the chat display
            self.chat_display.configure(state='normal')
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.configure(state='disabled')
            
            # Show confirmation
            messagebox.showinfo("History Cleared", "All chat history has been deleted.")
            
            # Re-add the initial greeting
            greeting = f"Hello {self.username}, I'm your AI chatbot. Your chat history has been cleared."
            self.display_message("AI", greeting)
        else:
            messagebox.showerror("Error", "Failed to clear chat history")

    def logout(self):
        # Save any pending message
        current_message = self.user_input.get().strip()
        if current_message:
            save_message_to_history(self.user_id, "You", current_message)
        
        # Clear the chat interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Return to login page
        from main import AppController
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
            self.user_input.delete(0, tk.END)
            self.root.after(2000, self.root.destroy)
            return
            
        self.display_message("You", user_text)
        save_message_to_history(self.user_id, "You", user_text)
        
        try:
            # Get AI response
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_text}]
            )
            ai_response = response.choices[0].message.content.strip()
            self.display_message("AI", ai_response)
            save_message_to_history(self.user_id, "AI", ai_response)
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.display_message("AI", error_msg)
        
        self.user_input.delete(0, tk.END)
    
    def load_chat_history(self):
        history = load_chat_history(self.user_id)
        for sender, message in history:
            self.display_message(sender, message)