import tkinter as tk
from gui.login import LoginPage
from database import initialize_database

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
        from gui.chat import ChatBotGUI
        self.chatbot = ChatBotGUI(self.root, username, user_id)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()