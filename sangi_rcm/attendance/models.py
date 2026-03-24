# attendance/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ==========================================
# 1. THE USER PROFILE
# ==========================================
class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to='master_ids/', blank=True, null=True)
    is_hr = models.BooleanField(default=False)
    is_accounts = models.BooleanField(default=False)
    is_hod = models.BooleanField(default=False)

   # 🟢 HR DOCUMENT VAULT FILES
    resume_cv = models.FileField(upload_to='employee_docs/cvs/', null=True, blank=True)
    aadhar_card = models.FileField(upload_to='employee_docs/aadhar/', null=True, blank=True)
    pan_card_doc = models.FileField(upload_to='employee_docs/pan/', null=True, blank=True)

    # 🟢 ANNEXURE / BANK DETAILS
    tenth_mark = models.FileField(upload_to='employee_docs/10th/', null=True, blank=True)
    twelfth_mark = models.FileField(upload_to='employee_docs/12th/', null=True, blank=True)
    graduation = models.FileField(upload_to='employee_docs/grad/', null=True, blank=True)
    experience_letter = models.FileField(upload_to='employee_docs/exp/', null=True, blank=True)
    passbook = models.FileField(upload_to='employee_docs/passbook/', null=True, blank=True)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # (Deleted the duplicate!)
    beneficiary_name = models.CharField(max_length=150, null=True, blank=True, help_text="Name exactly as per bank")
    bank_account = models.CharField(max_length=50, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)
    branch_code = models.CharField(max_length=20, null=True, blank=True)
    account_type = models.CharField(max_length=20, choices=[('Savings', 'Savings'), ('Current', 'Current')], default='Savings')
    
    pan_number = models.CharField(max_length=20, null=True, blank=True)
    uan_number = models.CharField(max_length=30, null=True, blank=True)
    master_photo = models.ImageField(upload_to='master_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.emp_id})"


# ==========================================
# 2. THE ATTENDANCE TABLE
# ==========================================
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'), 
        ('L', 'Late'), 
        ('A', 'Absent'), 
        ('H', 'Half Day'), 
        ('W', 'Week-Off'),
        ('E', 'Early Leave'),
        ('M', 'Missed Swap'),       # ⚠️ NEW: Panic Button Status
        ('O', 'Official Holiday')   # 🎉 NEW: Company Event/Holiday
    ]
    
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now) 
    
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    
    # Security Smart Lock Fields
    selfie = models.ImageField(upload_to='attendance_selfies/', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    
    # 🟢 NEW FIELD: To track Face vs Fingerprint
    punch_method = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., Face, Fingerprint, Card")

    # 📝 Missed Swap Note (Employee's excuse)
    employee_note = models.CharField(max_length=255, null=True, blank=True) 

    # 🛡️ HR Audit Trail
    is_hr_edited = models.BooleanField(default=False)
    edit_reason = models.CharField(max_length=255, null=True, blank=True) 

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.user.first_name} - {self.date} ({self.status})"


# ==========================================
# 3. THE LEAVE APPLICATION TABLE
# ==========================================
class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'), 
        ('Approved', 'Approved'), 
        ('Rejected', 'Rejected')
    ]

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.user.first_name} - {self.subject}"


# ==========================================
# 4. COMPANY CALENDAR (For Auto-Presents)
# ==========================================
class CompanyHoliday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=200) # e.g., "Diwali", "Founder's Day"
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.date})"


class PayrollUpdateRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending Admin Approval'),
        ('Approved', 'Approved & Applied'),
        ('Rejected', 'Rejected'),
    )
    employee = models.ForeignKey('EmployeeProfile', on_delete=models.CASCADE, related_name='payroll_requests')
    
    # 🟢 All the Annexure Fields Accounts might want to change
    proposed_base_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    proposed_pan_number = models.CharField(max_length=20, null=True, blank=True)
    proposed_bank_account = models.CharField(max_length=50, null=True, blank=True)
    proposed_ifsc_code = models.CharField(max_length=20, null=True, blank=True)
    proposed_uan_number = models.CharField(max_length=30, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    requested_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payroll Update: {self.employee.user.first_name} ({self.status})"


# ==========================================
# 5. SALARY UPDATE REQUEST
# ==========================================
class SalaryUpdateRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending Admin Approval'),
        ('Approved', 'Approved & Applied'),
        ('Rejected', 'Rejected'),
    )
    employee = models.ForeignKey('EmployeeProfile', on_delete=models.CASCADE, related_name='salary_requests')
    proposed_salary = models.DecimalField(max_digits=12, decimal_places=2, help_text='The new salary requested by Accounts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    requested_on = models.DateTimeField(auto_now_add=True)
    resolved_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Salary Update: {self.employee.user.first_name} ({self.status})"

    
# 🟢 THIS MUST BE ABOVE THE RESIGNATION REQUEST CLASS
class ResignationStatus(models.TextChoices):
    PENDING_HR = 'PENDING_HR', 'Pending HR Approval'
    APPROVED_HR = 'APPROVED_HR', 'Approved by HR (Pending Admin)'
    REJECTED_HR = 'REJECTED_HR', 'Rejected by HR'
    APPROVED_ADMIN = 'APPROVED_ADMIN', 'Notice Period Active'
    SHIFT_COMPLETED = 'SHIFT_COMPLETED', 'Shift Completed (Inactive)'
    REJECTED_ADMIN = 'REJECTED_ADMIN', 'Rejected by Admin'

# 🟢 THIS COMES SECOND
class ResignationRequest(models.Model):
    employee = models.ForeignKey('EmployeeProfile', on_delete=models.CASCADE, related_name='resignations')
    subject = models.CharField(max_length=200, help_text="e.g. Resignation - [Your Name]")
    description = models.TextField(help_text="Detailed reason for resignation")
    applied_date = models.DateField(default=timezone.now, help_text="Date resignation was officially applied")
    
    hr_status = models.CharField(max_length=20, choices=ResignationStatus.choices, default=ResignationStatus.PENDING_HR)
    hr_rejection_reason = models.TextField(blank=True, null=True, help_text="Required if HR rejects")
    hr_approved_on = models.DateTimeField(blank=True, null=True)
    
    admin_status = models.CharField(max_length=20, choices=ResignationStatus.choices, default=ResignationStatus.PENDING_HR)
    admin_approved_on = models.DateTimeField(blank=True, null=True)
    
    notice_period_end_date = models.DateField(blank=True, null=True, help_text="Automatically calculated upon Admin Approval")
    is_employee_inactive = models.BooleanField(default=False, help_text="System automatically sets to TRUE after notice period ends.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'is_employee_inactive')

    def __str__(self):
        return f"{self.employee.user.first_name} - {self.get_hr_status_display()}"
    
class CompanySettings(models.Model):
    company_name = models.CharField(max_length=255, default="SANGI RCM")
    company_account_no = models.CharField(max_length=50, help_text="Remitter Account Number (e.g., Company Bank A/C)")
    company_account_type = models.CharField(max_length=50, default="Current", help_text="e.g., Current, Savings")
    debit_account = models.CharField(max_length=50, help_text="Debit Account Number for the Annexure")

    class Meta:
        verbose_name = "Global Company Setting"
        verbose_name_plural = "Global Company Settings"

    def __str__(self):
        return "Company Bank & Setup Details"
    
class EmployeeDocument(models.Model):
    employee = models.OneToOneField('EmployeeProfile', on_delete=models.CASCADE, related_name='documents')
    
    # The 8 Mandatory Files
    photo = models.FileField(upload_to='employee_docs/photos/', null=True, blank=True)
    tenth_mark = models.FileField(upload_to='employee_docs/10th/', null=True, blank=True)
    twelfth_mark = models.FileField(upload_to='employee_docs/12th/', null=True, blank=True)
    graduation = models.FileField(upload_to='employee_docs/graduation/', null=True, blank=True)
    experience_letter = models.FileField(upload_to='employee_docs/experience/', null=True, blank=True)
    pan_card = models.FileField(upload_to='employee_docs/pan/', null=True, blank=True)
    aadhaar_card = models.FileField(upload_to='employee_docs/aadhaar/', null=True, blank=True)
    
    # 🟢 This is the ONLY file Accounts will be allowed to see!
    passbook = models.FileField(upload_to='employee_docs/passbook/', null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Documents for {self.employee.user.first_name}"


# 🟢 1. THE COMPANY NOTICE BOARD
class CompanyNotice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Targeting Options
    TARGET_CHOICES = [
        ('All', 'All Employees'),
        ('Department', 'Specific Department'),
        ('Employee', 'Specific Employee')
    ]
    target_audience = models.CharField(max_length=50, choices=TARGET_CHOICES, default='All')
    
    # If targeting a specific department or person, we save it here
    target_department = models.CharField(max_length=100, null=True, blank=True)
    target_employee = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='targeted_notices')
    
    # Who posted it?
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notices_posted')

    def __str__(self):
        return self.title


# 🟢 2. DEPENDENT DETAILS (Up to 3 per employee)
class DependentDetail(models.Model):
    employee = models.ForeignKey('EmployeeProfile', on_delete=models.CASCADE, related_name='dependents')
    name = models.CharField(max_length=150)
    relation = models.CharField(max_length=50)
    dob = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.relation}) - {self.employee.user.first_name}"


# 🟢 3. BACKGROUND VERIFICATION (Past Experience)
class BackgroundVerification(models.Model):
    employee = models.OneToOneField('EmployeeProfile', on_delete=models.CASCADE, related_name='bgv_detail')
    
    # Reference Details
    ref_name = models.CharField(max_length=150, null=True, blank=True)
    ref_post = models.CharField(max_length=100, null=True, blank=True)
    ref_organization = models.CharField(max_length=150, null=True, blank=True)
    ref_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Is it verified by HR?
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"BGV: {self.employee.user.first_name} {self.employee.user.last_name}"


class AllowedIP(models.Model):
    ip_address = models.CharField(max_length=45, unique=True)
    description = models.CharField(max_length=100, blank=True, help_text="e.g. Main Router, Ground Floor")
    created_at = models.DateTimeField(auto_now_add=True)

    def __clstr__(self):
        return f"{self.ip_address} ({self.description})"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.user.first_name}: {self.message}"
    

# 2. THE TASK ENGINE
class Task(models.Model):
    assigned_by = models.ForeignKey(EmployeeProfile, related_name='assigned_tasks', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(EmployeeProfile, related_name='received_tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Pending')

class TaskRevert(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='revert')
    employee_notes = models.TextField(blank=True, null=True)
    attached_file = models.FileField(upload_to='task_files/', blank=True, null=True) # 🟢 FILE UPLOADS!
    submitted_on = models.DateTimeField(auto_now_add=True)
    hod_status = models.CharField(max_length=20, choices=[('Pending Review', 'Pending Review'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending Review')
    rejection_reason = models.TextField(blank=True, null=True)

# 3. THE GRIEVANCE & POSH PORTAL
class Grievance(models.Model):
    CATEGORY_CHOICES = [
        ('General', 'General Grievance'),
        ('POSH', 'POSH - Harassment Report'),
        ('Payroll', 'Payroll Issue'),
    ]
    submitted_by = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, null=True)

# 4. COMPANY RULES & POLICIES
class CompanyPolicy(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Write the policy or rules here.")
    is_posh_guideline = models.BooleanField(default=False, help_text="Check this if this is a POSH specific policy.")
    last_updated = models.DateTimeField(auto_now=True)