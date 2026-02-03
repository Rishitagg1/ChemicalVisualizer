import json
import csv
import os
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .utils import process_dataset  # Ensure backend/api/utils.py exists!

# File to store users
USER_DB_FILE = 'users.csv'

def get_users():
    """Helper to read users from CSV"""
    users = []
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, mode='r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(row)
    return users

def save_user(user_data):
    """Helper to append a new user to CSV"""
    file_exists = os.path.exists(USER_DB_FILE)
    with open(USER_DB_FILE, mode='a', newline='') as f:
        fieldnames = ['name', 'email', 'password', 'phone', 'institute']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(user_data)

def update_user_in_csv(updated_data):
    """Helper to update a specific user in CSV"""
    users = get_users()
    updated = False
    
    # Update the user list in memory
    for user in users:
        if user['email'] == updated_data['email']:
            user.update(updated_data) # Update fields
            updated = True
            break
            
    # Write back to file if change occurred
    if updated:
        with open(USER_DB_FILE, mode='w', newline='') as f:
            fieldnames = ['name', 'email', 'password', 'phone', 'institute']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)
            
    return updated

# ==========================================
# 1. DYNAMIC UPLOAD VIEW
# ==========================================
@method_decorator(csrf_exempt, name='dispatch')
class UploadView(View):
    def post(self, request):
        if request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            # Use our universal parser from utils.py
            data = process_dataset(uploaded_file, uploaded_file.name)
            return JsonResponse(data)
        return JsonResponse({"error": "No file uploaded"}, status=400)

# ==========================================
# 2. SIGNUP VIEW
# ==========================================
@method_decorator(csrf_exempt, name='dispatch')
class SignupView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            # Check duplicates
            existing_users = get_users()
            if any(u['email'] == email for u in existing_users):
                return JsonResponse({"error": "User already exists"}, status=400)

            # Save to CSV
            new_user = {
                'name': data.get('name'),
                'email': email,
                'password': data.get('password'),
                'phone': data.get('phone', ''),
                'institute': data.get('institute', '')
            }
            save_user(new_user)
            
            return JsonResponse({"message": "User registered successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# ==========================================
# 3. LOGIN VIEW
# ==========================================
# ... (Keep imports at the top)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            # =====================================================
            # 🔑 MASTER LOGIN KEY (Hardcoded Admin)
            # =====================================================
            # You can change these strings to anything you want!
            MASTER_ID = "admin@gmail.com" 
            MASTER_PASS = "admin123"

            if email == MASTER_ID and password == MASTER_PASS:
                return JsonResponse({
                    "message": "Master Access Granted",
                    "name": "Super Admin",
                    "role": "admin",      # <--- This tells frontend to show Admin Panel
                    "username": "admin",
                    "institute": "Headquarters"
                }, status=200)
            # =====================================================

            # ... (Rest of the normal user CSV check logic follows below) ...
            
            users = get_users()
            user = next((u for u in users if u['email'] == email and u['password'] == password), None)
            
            if user:
                return JsonResponse({
                    "message": "Login Successful",
                    "name": user['name'],
                    "role": "user",       # <--- Normal user role
                    "username": email.split('@')[0],
                    "phone": user.get('phone', ''),
                    "institute": user.get('institute', '')
                }, status=200)
            
            return JsonResponse({"error": "Invalid Credentials"}, status=401)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# ==========================================
# 4. UPDATE PROFILE VIEW (The Missing One)
# ==========================================
@method_decorator(csrf_exempt, name='dispatch')
class UpdateProfileView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email") # Email is the ID
            
            if not email:
                return JsonResponse({"error": "Email required to identify user"}, status=400)

            # Update CSV
            success = update_user_in_csv(data)
            
            if success:
                return JsonResponse({
                    "message": "Profile Updated",
                    "name": data.get("name"),
                    "email": email,
                    "phone": data.get("phone"),
                    "institute": data.get("institute")
                }, status=200)
            else:
                return JsonResponse({"error": "User not found"}, status=404)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)