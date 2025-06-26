import tkinter as tk
from tkinter import ttk, messagebox
from auth import authenticate, register

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
        
        user_id = authenticate(username, password)
        if user_id:
            self.on_login_success(username, user_id)
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def attempt_signup(self):
        username = self.signup_username.get().strip()
        password = self.signup_password.get().strip()
        confirm_password = self.signup_confirm_password.get().strip()
        
        success, message = register(username, password, confirm_password)
        if success:
            messagebox.showinfo("Success", message)
            self.notebook.select(0)  # Switch to login tab
            self.login_username.delete(0, tk.END)
            self.login_username.insert(0, username)
            self.login_password.focus()
        else:
            messagebox.showerror("Error", message)