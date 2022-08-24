from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Photo, Journal, City
from django.contrib.auth.models import Group, User

admin.site.unregister(Group)
admin.site.unregister(User)


class CityInLine(admin.StackedInline):
    model = City.operators.through
    verbose_name = 'Связь Оператор-Город'
    verbose_name_plural = 'Связи Оператор-Город'
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональные данные", {"fields": ("first_name", "last_name", "email")}),
    )
    inlines = [CityInLine]


class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city_code', 'city_name', 'city_operators')
    list_display_links = ('city_code',)

    def city_operators(self, obj):
        return [c.username for c in obj.operators.all()]

    city_operators.short_description = 'Операторы'


class JournalAdmin(admin.ModelAdmin):
    list_display = ('id', 'journal_name', 'journal_city', 'journal_owner', 'filled_pages', 'total_pages', 'time_create')
    list_display_links = ('journal_name',)
    list_filter = ('journal_city', 'journal_owner', 'time_create')


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'photo_name', 'journal', 'page_in_journal', 'photo_image')
    list_display_links = ('photo_name',)

    def journal(self, obj):
        return obj.journal.journal_city

    journal.admin_order_field = 'journal__journal_city'
    journal.short_description = 'Город'


admin.site.register(Photo, PhotoAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(City, CityAdmin)
