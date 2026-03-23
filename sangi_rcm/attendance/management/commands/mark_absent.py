from django.core.management.base import BaseCommand
from attendance.models import EmployeeProfile, Attendance, LeaveRequest, CompanyHoliday
from datetime import datetime

class Command(BaseCommand):
    help = 'Runs at 11:59 PM: Marks Sundays (W), Holidays (O), and Absents (A)'

    def handle(self, *args, **kwargs):
        today = datetime.now().date()
        
        # 1. WHAT DAY IS IT?
        is_sunday = today.weekday() == 6  # In Python, Monday is 0 and Sunday is 6
        
        # 2. IS IT A HOLIDAY?
        holiday = CompanyHoliday.objects.filter(date=today).first()
        is_holiday = holiday is not None

        # 3. GRAB ALL ACTIVE EMPLOYEES (Skip HR and Accounts)
        employees = EmployeeProfile.objects.filter(is_hr=False, is_accounts=False, user__is_active=True)
        
        marked_w = 0
        marked_o = 0
        marked_a = 0

        for emp in employees:
            # Check 1: Did they already punch in today?
            if Attendance.objects.filter(employee=emp, date=today).exists():
                continue
            
            # Check 2: Are they on an Approved Leave right now?
            on_leave = LeaveRequest.objects.filter(
                employee=emp, 
                status='Approved',
                start_date__lte=today, 
                end_date__gte=today
            ).exists()
            
            if on_leave:
                continue # Skip them entirely! We don't mark them absent.

            # THE FINAL VERDICT:
            if is_holiday:
                # Give them an 'O' and write the holiday name in their note!
                Attendance.objects.create(employee=emp, date=today, status='O', employee_note=holiday.name)
                marked_o += 1
            elif is_sunday:
                # Give them a 'W' for the weekend
                Attendance.objects.create(employee=emp, date=today, status='W')
                marked_w += 1
            else:
                # Standard workday, no punch, no leave = Absent
                Attendance.objects.create(employee=emp, date=today, status='A')
                marked_a += 1
                
        self.stdout.write(self.style.SUCCESS(f'✅ Midnight Script Complete! Absents: {marked_a} | Sundays: {marked_w} | Holidays: {marked_o}'))