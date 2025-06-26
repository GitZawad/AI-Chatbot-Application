from database import get_user, verify_password, create_user

def authenticate(username, password):
    user_data = get_user(username)
    if not user_data:
        return None
    
    user_id, stored_hash, salt = user_data
    if verify_password(stored_hash, salt, password):
        return user_id
    return None

def register(username, password, confirm_password):
    if not username or not password or not confirm_password:
        return (False, "Please fill in all fields")
    
    if password != confirm_password:
        return (False, "Passwords don't match")
    
    if len(password) < 6:
        return (False, "Password must be at least 6 characters")
    
    if get_user(username):
        return (False, "Username already exists")
    
    user_id = create_user(username, password)
    if user_id:
        return (True, "Account created successfully!")
    else:
        return (False, "Failed to create account")