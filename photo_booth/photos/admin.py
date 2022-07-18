from django.contrib import admin
from .models import User, JournalPhoto, Journals, Cities

admin.site.register(User)
admin.site.register(JournalPhoto)
admin.site.register(Journals)
admin.site.register(Cities)

