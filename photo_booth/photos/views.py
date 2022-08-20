from datetime import datetime

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

from photos.models import City, Photo, Journal, TOTAL_PAGES


def main_page(request):
    city = City.objects.all()
    context = {'city': city}
    return render(request, 'index.html', context)


def registry(request, city_code):
    city = City.objects.get(city_code=city_code)
    journal = city.journal_set.all()
    context = {'journal': journal, 'city': city}
    return render(request, 'registry.html', context)


def registry_further(request, city_code, journal_id):
    city = City.objects.get(city_code=city_code)
    journal = Journal.objects.get(id=journal_id)
    photos = journal.photo_set.all()
    context = {
        'journal': journal,
        'city': city,
        'photos': photos,
    }
    return render(request, 'registry_further.html', context)


def furthermore(request, city_code, journal_id, photo_id):
    photo = Photo.objects.get(id=photo_id)
    context = {
        'photo': photo,
    }
    return render(request, 'image.html', context)


def main_manage(request):
    if request.user.is_authenticated:
        return cities_selection(request)
    return redirect('/manage/login')


def cities_selection(request):
    available_cities = City.objects.filter(operators=request.user.id)
    context = {
        'cities_set': available_cities,
    }
    if len(available_cities) == 0:
        context.update({'message': 'У тебя нет городов, мой друг'})
    if len(available_cities) == 1:
        return get_journals(request, available_cities[0].id)
    return render(request, 'cities.html', context)


def get_journals(request, city_id):
    city = City.objects.get(id=city_id)
    user = User.objects.get(id=request.user.pk)
    journals = Journal.objects.filter(journal_city=city)
    message = f"Количество журналов: {len(journals)}."
    last_journal = None

    context = {
        'message': message,
        'current': f'Текущий город: {city}',
    }

    if journals:
        first_journal_pages = set()
        for journal in journals:
            first_journal_pages.add(int(journal.journal_name.split('-')[0]))
        last_journal = journals.get(journal_name=f'{max(first_journal_pages)}-{max(first_journal_pages) + TOTAL_PAGES - 1}')
        last_journal_photos = last_journal.photo_set.all()
        context['message'] += f" В текущем журнале {len(last_journal_photos)} фото."
        if len(last_journal_photos) == last_journal.total_pages:
            last_journal = None

    if request.method == "POST":
        image = request.FILES.get('image')

        if not last_journal:
            last_journal = Journal.objects.create(
                journal_city=city,
                journal_owner_id=user.id,
                time_create=datetime.now(),
            )

        Photo.objects.create(
            journal=last_journal,
            photo_image=image,
            time_create=datetime.now(),
        )

        last_journal.update_values()

        messages.info(request, 'Удачно загружено 1 фото')
        return redirect('journal', city_id)

    return render(request, 'journal.html', context)
