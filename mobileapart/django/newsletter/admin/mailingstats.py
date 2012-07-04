from django.contrib import admin

class MailingStatsAdmin(admin.ModelAdmin):
    list_display = ('contact', 'sent', 'opened','smtp_error')
