import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from attendance.models import Attendance, EmployeeProfile
# Add any other necessary imports

class Command(BaseCommand):
    help = 'Fetches the latest attendance logs from the easy WDMS API'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting WDMS API Sync...")

        # 1. API Credentials & Endpoints (You will get these from the vendor)
        WDMS_URL = "http://vendor-wdms-url.com/api/transactions/"
        API_TOKEN = "your_api_token_here"

        headers = {
            "Authorization": f"Token {API_TOKEN}",
            "Content-Type": "application/json"
        }

        try:
            # 2. Fetch the Data
            # Note: We will likely need to add parameters like ?start_time=... to only get new logs
            response = requests.get(WDMS_URL, headers=headers)
            
            if response.status_code == 200:
                logs = response.json().get('data', [])
                
                # 3. Process and Save the Data
                new_punches = 0
                for log in logs:
                    emp_id = log.get('emp_code')
                    punch_time_str = log.get('punch_time')
                    verify_type = log.get('verify_mode') # Usually 1=Finger, 15=Face
                    
                    # Convert verify_type integer to text
                    if verify_type == 1:
                        method = "Fingerprint"
                    elif verify_type == 15:
                        method = "Face"
                    else:
                        method = "Other"

                    # Parse datetime
                    punch_dt = datetime.strptime(punch_time_str, '%Y-%m-%d %H:%M:%S')
                    punch_date = punch_dt.date()
                    punch_time = punch_dt.time()

                    # Find Employee
                    employee = EmployeeProfile.objects.filter(user__username=emp_id).first()
                    
                    if employee:
                        # Logic to create or update the Attendance record goes here!
                        # (e.g., checking if it's a check_in or check_out)
                        new_punches += 1

                self.stdout.write(self.style.SUCCESS(f"Successfully synced {new_punches} new punches."))
            else:
                self.stdout.write(self.style.ERROR(f"API Error: {response.status_code}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Sync Failed: {str(e)}"))