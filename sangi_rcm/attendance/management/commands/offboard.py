from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import ResignationRequest

class Command(BaseCommand):
    help = 'Automatically locks out employees whose 30-day notice period has ended.'

    def handle(self, *args, **kwargs):
        today = timezone.localtime(timezone.now()).date()
        
        # Find everyone whose notice period is today (or in the past) and is still active
        expired_resignations = ResignationRequest.objects.filter(
            admin_status='APPROVED_ADMIN',
            is_employee_inactive=False,
            notice_period_end_date__lte=today
        )

        count = 0
        for req in expired_resignations:
            # 1. Lock the Django User Account (They can never log in again)
            user = req.employee.user
            user.is_active = False
            user.save()
            
            # 2. Mark the offboarding as 100% complete
            req.is_employee_inactive = True
            req.hr_status = 'SHIFT_COMPLETED'
            req.admin_status = 'SHIFT_COMPLETED'
            req.save()
            
            count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Auto-Offboarding Complete: Locked out {count} employees today!"))