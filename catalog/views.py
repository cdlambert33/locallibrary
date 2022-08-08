from itertools import count
from django.db.models import Count
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre

# Create your views here.

def index(request):

    # generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # available books (stats = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # the 'all()' is implied by default
    num_authors = Author.objects.count()

  

    # get count of each genre
    num_genre = Genre.objects.all().values('name')
    genre_names = []
    for i in num_genre:
        genre_names.append(i['name'])

    for i in num_genre:
        genre_names.append(i)

    genres = Book.objects.all().order_by('genre').values('genre').annotate(count=Count('genre'))

    total_genre_count = len(num_genre)
    genre_counts = {}
    keys = ['name','count']

    for i in range(total_genre_count):
        name = genre_names[i]
        count = genres[i]['count']
        values = [name,count]
        genre_counts[i] = dict(zip(keys, values))
    

    num_scifi = Book.objects.filter(genre__name__exact='Science Fiction').count()
    num_fantasy = Book.objects.filter(genre__name__exact='Fantasy').count()
    num_nonfi = Book.objects.filter(genre__name__exact='Nonfiction').count()
    num_comics = Book.objects.filter(genre__name__exact='Comics').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_scifi': num_scifi,
        'num_fantasy': num_fantasy,
        'num_nonfi': num_nonfi,
        'num_comics': num_comics,
        'num_genre': num_genre,
        'genres': genres,
        'genre_counts': genre_counts,
        'range': (1,total_genre_count),
    }

    # render the HTML template index.html with the dat in the context variable
    return render(request, 'index.html', context=context)