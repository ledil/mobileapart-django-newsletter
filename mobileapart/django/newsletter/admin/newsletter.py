from django.contrib import admin

class NewsletterAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('uuid', 'mailing_list', 'status','template_body','template_subject','template_base_body',
                    'sending_date', 'creation_date', 'modification_date')
    list_filter = ('status', 'sending_date', 'creation_date', 'modification_date')
    search_fields = ('header_sender', 'header_reply')

    fieldsets = ((None, {'fields':('template_base_body', 'template_subject', 'template_body', 'dictionary','mailing_list','sending_date','status','test_contacts','header_sender','header_reply')}),)
