from django.contrib import admin
from .models import EmployeeProfile, Attendance, LeaveRequest, CompanyHoliday
from django.utils import timezone
from datetime import timedelta
from .models import CompanySettings # Make sure to import it!
from .models import CompanyNotice, DependentDetail, BackgroundVerification, EmployeeDocument
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.contrib import messages
# Just add ResignationStatus to your existing import line!
from .models import ResignationRequest, PayrollUpdateRequest, ResignationStatus

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'emp_id', 'department', 'is_hr')
    list_filter = ('is_hr', 'department')
    search_fields = ('user__username', 'emp_id')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status')
    list_filter = ('status', 'date')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'subject', 'start_date', 'end_date', 'status')
    list_filter = ('status',)

# ==========================================
# 🟢 NEW: COMPANY HOLIDAY ADMIN
# ==========================================
@admin.register(CompanyHoliday)
class CompanyHolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    list_filter = ('date',)
    search_fields = ('name',)


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'company_account_no']

    # 🟢 SMART LOGIC: Prevent adding multiple company settings!
    def has_add_permission(self, request):
        # If one already exists, hide the "Add" button
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
    
@admin.register(CompanyNotice)
class CompanyNoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'target_audience', 'created_at')
    list_filter = ('target_audience', 'created_at')
    search_fields = ('title', 'message')

@admin.register(DependentDetail)
class DependentDetailAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name', 'relation', 'dob')
    search_fields = ('employee__user__first_name', 'name')

@admin.register(BackgroundVerification)
class BackgroundVerificationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'ref_name', 'ref_organization', 'ref_phone')
    search_fields = ('employee__user__first_name', 'ref_organization')

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    # Removed 'doc_type' so Django stops panicking!
    list_display = ('employee', 'uploaded_at')

# ==========================================
# 1. FIXED RESIGNATION REQUEST ADMIN
# ==========================================
@admin.register(ResignationRequest)
class ResignationRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'applied_date', 'hr_status', 'admin_status', 'admin_actions')
    list_filter = ('hr_status', 'admin_status')
    
    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return ('employee', 'applied_date')
        return ('applied_date',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:req_id>/approve/', self.admin_site.admin_view(self.approve_resignation), name='resignation-approve'),
            path('<int:req_id>/reject/', self.admin_site.admin_view(self.reject_resignation), name='resignation-reject'),
        ]
        return custom_urls + urls

    def admin_actions(self, obj):
        # 🟢 EXACT MATCH: Check against your models.py TextChoices
        if obj.admin_status not in [ResignationStatus.APPROVED_ADMIN, ResignationStatus.REJECTED_ADMIN]:
            return format_html(
                '<a class="button" style="background-color: #22c55e; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;" href="{}">Approve</a>&nbsp;&nbsp;'
                '<a class="button" style="background-color: #ef4444; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;" href="{}">Reject</a>',
                reverse('admin:resignation-approve', args=[obj.pk]),
                reverse('admin:resignation-reject', args=[obj.pk])
            )
        return format_html('<b style="color: gray;">{}</b>', 'Actioned')
    
    admin_actions.short_description = '1-Click Actions'

    def approve_resignation(self, request, req_id):
        obj = self.get_object(request, req_id)
        # 🟢 EXACT MATCH
        obj.admin_status = ResignationStatus.APPROVED_ADMIN
        obj.save()
        messages.success(request, f"✅ APPROVED resignation for {obj.employee}.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    def reject_resignation(self, request, req_id):
        obj = self.get_object(request, req_id)
        # 🟢 EXACT MATCH
        obj.admin_status = ResignationStatus.REJECTED_ADMIN
        obj.save()
        messages.error(request, f"❌ REJECTED resignation for {obj.employee}.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))


# ==========================================
# 2. NEW PAYROLL UPDATE REQUEST ADMIN
# ==========================================
@admin.register(PayrollUpdateRequest)
class PayrollUpdateRequestAdmin(admin.ModelAdmin):
    # Adjust 'created_at' if you named the date field something else in models.py!
    list_display = ('employee', 'status', 'admin_actions') 
    list_filter = ('status',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('employee',) # Protect employee name if editing
        return ()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:req_id>/payroll-approve/', self.admin_site.admin_view(self.approve_payroll), name='payroll-approve'),
            path('<int:req_id>/payroll-reject/', self.admin_site.admin_view(self.reject_payroll), name='payroll-reject'),
        ]
        return custom_urls + urls

    def admin_actions(self, obj):
        # Only show buttons if it is Pending
        if obj.status.upper() == 'PENDING': 
            return format_html(
                '<a class="button" style="background-color: #22c55e; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;" href="{}">Approve</a>&nbsp;&nbsp;'
                '<a class="button" style="background-color: #ef4444; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;" href="{}">Reject</a>',
                reverse('admin:payroll-approve', args=[obj.pk]),
                reverse('admin:payroll-reject', args=[obj.pk])
            )
        return format_html('<b style="color: gray;">{}</b>', 'Actioned')
    
    admin_actions.short_description = '1-Click Actions'

    def approve_payroll(self, request, req_id):
        obj = self.get_object(request, req_id)
        obj.status = 'Approved'
        obj.save()
        messages.success(request, f"✅ APPROVED payroll update for {obj.employee}.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    def reject_payroll(self, request, req_id):
        obj = self.get_object(request, req_id)
        obj.status = 'Rejected'
        obj.save()
        messages.error(request, f"❌ REJECTED payroll update for {obj.employee}.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))
    

from .models import AllowedIP

# 🟢 This adds the IP manager directly into your secure Django Admin portal
@admin.register(AllowedIP)
class AllowedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'description', 'created_at')
    search_fields = ('ip_address', 'description')