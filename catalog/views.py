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

    num_per_genre = []

    # get count of each genre

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
    }

    # render the HTML template index.html with the dat in the context variable
    return render(request, 'index.html', context=context)