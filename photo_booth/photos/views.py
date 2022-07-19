from datetime import datetime

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

from photos.models import Cities, JournalPhoto, Journals


def main_page(request):
    if request.user.is_authenticated:
        return cities_selection(request)
    return redirect('/login')


def cities_selection(request):
    available_cities = Cities.objects.filter(operators=request.user.id)
    context = {
        'cities_set': available_cities,
    }
    if len(available_cities) == 0:
        context.update({'message': 'You have no cities, my friend.'})
    if len(available_cities) == 1:
        return get_journals(request, available_cities[0].id)
    return render(request, 'cities.html', context)


def get_journals(request, city_id):
    city = Cities.objects.get(id=city_id)
    user = User.objects.get(id=request.user.pk)
    journals = Journals.objects.filter(journal_city=city).filter(journal_owner=user)
    message = f"You have {len(journals)} journals."
    last_journal = None

    context = {
        'message': message,
        'current': f'Current city is {city}',
    }

    if journals:
        last_journal = journals.latest('time_create')
        last_journal_photos = JournalPhoto.objects.filter(j_photo_journal=last_journal.id)
        context['message'] += f" Current journal has {len(last_journal_photos)} photos in it."
        if len(last_journal_photos) == 3:
            last_journal = None

    if request.method == "POST":
        image = request.FILES.get('image')
        if not last_journal:
            last_journal = Journals.objects.create(
                journal_city=city,
                journal_owner_id=user.id,
                time_create=datetime.now()
            )
        JournalPhoto.objects.create(
            j_photo_journal=last_journal,
            j_photo_image=image,
            time_create=datetime.now()
        )
        messages.info(request, 'You have successfully uploaded 1 photo')
        return redirect('journal', city_id)

    return render(request, 'journal.html', context)
