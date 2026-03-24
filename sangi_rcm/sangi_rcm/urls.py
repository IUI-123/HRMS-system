# sangi_rcm/urls.py
from django.contrib import admin
from django.urls import path, include
from attendance import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/login/', views.login_view, name='admin_login_hijack'),
    path('admin/logout/', views.logout_view, name='admin_logout_hijack'),
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),

    # ── EMPLOYEE ──────────────────────────────────────────
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
    path('dashboard/apply-leave/', views.apply_leave, name='apply_leave'),
    path('dashboard/employee/submit-resignation/', views.submit_resignation, name='submit_resignation'),
    path('dashboard/employee/grievance/', views.grievance_view, name='grievance'),
    path('dashboard/employee/submit-grievance/', views.submit_grievance, name='submit_grievance'),

    # ── HR ────────────────────────────────────────────────
    path('dashboard/hr/', views.hr_dashboard, name='hr_dashboard'),
    path('dashboard/hr/update-leave/<int:leave_id>/<str:action>/', views.update_leave, name='update_leave'),
    path('dashboard/hr/update-leave/<int:leave_id>/', views.hr_update_leave, name='hr_update_leave'),
    path('dashboard/hr/add-employee/', views.add_employee, name='add_employee'),
    path('dashboard/hr/export/', views.export_attendance, name='export_attendance'),
    path('dashboard/hr/upload-documents/<int:emp_id>/', views.hr_upload_documents, name='hr_upload_documents'),
    path('dashboard/hr/get-docs/<int:emp_id>/', views.hr_get_employee_docs, name='hr_get_employee_docs'),
    path('dashboard/hr/delete-doc/<int:emp_id>/<str:doc_type>/', views.hr_delete_employee_doc, name='hr_delete_employee_doc'),
    path('dashboard/hr/notices/', views.hr_notice_board, name='hr_notice_board'),
    path('dashboard/hr/export-bgv/', views.export_bgv_pdf, name='export_bgv_pdf'),
    path('dashboard/hr/process-resignation/<int:req_id>/', views.hr_process_resignation, name='hr_process_resignation'),
    path('dashboard/hr/grievances/', views.hr_grievance_list, name='hr_grievance_list'),
    path('dashboard/hr/grievances/<int:pk>/update/', views.hr_grievance_update, name='hr_grievance_update'),

    # ── ACCOUNTS ──────────────────────────────────────────
    path('dashboard/accounts/', views.accounts_dashboard, name='accounts_dashboard'),
    path('dashboard/accounts/update-salary/<int:emp_id>/', views.update_base_salary, name='update_base_salary'),
    path('dashboard/accounts/payslip/<int:emp_id>/<int:month>/<int:year>/', views.generate_payslip, name='generate_payslip'),
    path('dashboard/accounts/export-annexure/', views.export_annexure_excel, name='export_annexure'),
    path('dashboard/accounts/update-employee/<int:emp_id>/', views.accounts_update_employee, name='accounts_update_employee'),

    path('dashboard/accounts/grievance/', views.accounts_grievance_view, name='accounts_grievance'),

    path('dashboard/accounts/grievance/', views.accounts_grievance_view, name='accounts_grievance'),

    path('dashboard/accounts/grievance/', views.accounts_grievance_view, name='accounts_grievance'),

    path('dashboard/policies/', views.company_policies_view, name='company_policies'),

    path('dashboard/accounts/grievance/', views.accounts_grievance_view, name='accounts_grievance'),

    path('dashboard/accounts/grievance/', views.accounts_grievance_view, name='accounts_grievance'),

    # ── HOD ───────────────────────────────────────────────
    path('dashboard/hod/', views.hod_dashboard, name='hod_dashboard'),

    # ── MISC ──────────────────────────────────────────────
    path('api/mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('hr-edit-attendance/', views.hr_edit_attendance, name='hr_edit_attendance'),
    path('missed-swap/', views.request_missed_swap, name='request_missed_swap'),
    path('hr-manual-entry/', views.hr_manual_entry, name='hr_manual_entry'),
    path('remove-employee/<str:emp_id>/', views.remove_employee, name='remove_employee'),
    path('hr/update-photo/<int:emp_id>/', views.hr_update_master_photo, name='hr_update_master_photo'),
    path('api/run-automation/', views.run_daily_automation, name='run_daily_automation'),
    path('api/notifications/', views.get_notifications, name='api_notifications'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)