from django.contrib import admin
from .models import User, JournalPhoto, Journals, Cities


class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'get_cities')
    list_display_links = ('username',)

    def get_cities(self, obj):
        return [c.city_name for c in Cities.objects.filter(operators=obj.id)]

    get_cities.short_description = 'Города'


class CitiesAdmin(admin.ModelAdmin):
    list_display = ('id', 'city_name', 'city_operators')
    list_display_links = ('city_name',)

    def city_operators(self, obj):
        return [c.username for c in obj.operators.all()]

    city_operators.short_description = 'Операторы'


class JournalsAdmin(admin.ModelAdmin):
    list_display = ('id', 'journal_city', 'journal_owner', 'time_create')
    list_display_links = ('id',)
    list_filter = ('journal_city', 'journal_owner', 'time_create')


class PhotosAdmin(admin.ModelAdmin):
    list_display = ('id', 'j_photo_journal', 'journal', 'j_photo_image')
    list_display_links = ('id',)

    def journal(self, obj):
        return obj.j_photo_journal.journal_city

    journal.admin_order_field = 'j_photo_journal__journal_city'
    journal.short_description = 'Город'


admin.site.register(User, UsersAdmin)
admin.site.register(JournalPhoto, PhotosAdmin)
admin.site.register(Journals, JournalsAdmin)
admin.site.register(Cities, CitiesAdmin)
