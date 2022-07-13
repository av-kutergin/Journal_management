from django.contrib import admin
from .models import Photo, Operators, JournalPhoto, Journals, Cities

admin.site.register(Photo)
admin.site.register(Operators)
admin.site.register(JournalPhoto)
admin.site.register(Journals)
admin.site.register(Cities)

