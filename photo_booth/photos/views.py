from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import BadRequest
from django.shortcuts import render, redirect
from django.contrib import messages

from photos.models import City, Photo, Journal


def main_page(request):
    city = City.objects.all()
    context = {'city': city}
    return render(request, 'index.html', context)


def registry(request, city_code):
    city = City.objects.get(city_code=city_code)
    journal = city.journal_set.all()
    context = {'journal': journal, 'city': city}
    return render(request, 'registry.html', context)


def registry_further(request, city_code, journal_name):
    city = City.objects.get(city_code=city_code)
    journal = Journal.objects.get(journal_city_id=city.pk, journal_name=journal_name)
    photos = journal.photo_set.all()
    context = {
        'journal': journal,
        'city': city,
        'photos': photos,
    }
    return render(request, 'registry_further.html', context)


def furthermore(request, city_code, journal_name, photo_id):
    photo = Photo.objects.get(id=photo_id)
    context = {
        'photo': photo,
    }
    return render(request, 'image.html', context)


def main_manage(request):
    if request.user.is_authenticated:
        return cities_selection(request)
    return redirect('/manage/login/')


def cities_selection(request):
    available_cities = City.objects.filter(operators=request.user.id)
    context = {
        'cities_set': available_cities,
    }
    if available_cities.count() == 0:
        context.update({'message': 'У тебя нет городов, мой друг'})
    if available_cities.count() == 1:
        return get_or_update_journals(request, available_cities[0].city_code)
    return render(request, 'cities.html', context)


def get_or_update_journals(request, city_code):
    city = City.objects.get(city_code=city_code)
    user = User.objects.get(id=request.user.pk)
    journals = Journal.objects.filter(journal_city=city)

    last_journal = Journal.get_last_journal(city)

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
        return redirect('journal', city_code)

    elif request.method == "GET":
        message = f"Количество журналов: {journals.count()}."
        context = {
            'message': message,
            'current': f'Текущий город: {city}',
        }
        if last_journal:
            last_journal_photos = last_journal.photo_set.all()
            context['message'] += f" В текущем журнале {last_journal_photos.count()} фото."

        return render(request, 'journal.html', context)

    else:
        raise BadRequest
