from django.contrib import admin
from .models import User, Photo, Journal, City


class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city_name', 'city_operators')
    list_display_links = ('city_name',)

    def city_operators(self, obj):
        return [c.username for c in obj.operators.all()]

    city_operators.short_description = 'Операторы'


class JournalAdmin(admin.ModelAdmin):
    list_display = ('id', 'journal_name', 'journal_city', 'journal_owner', 'filled_pages', 'total_pages', 'time_create')
    list_display_links = ('id',)
    list_filter = ('journal_city', 'journal_owner', 'time_create')


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'photo_name', 'journal', 'page_in_journal', 'photo_image')
    list_display_links = ('id',)

    def journal(self, obj):
        return obj.journal.journal_city

    journal.admin_order_field = 'journal__journal_city'
    journal.short_description = 'Город'

admin.site.register(Photo, PhotoAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(City, CityAdmin)
