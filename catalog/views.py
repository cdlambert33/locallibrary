from itertools import count
from django.db.models import Count
from django.shortcuts import render
from django.views import generic
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

    # get genre names and counts
    num_genre = Genre.objects.all().values('name')
    genre_names = []
    for i in num_genre:
        genre_names.append(i['name'])

    # gets the total count of each genre grouped by genre name
    genres = Book.objects.all().order_by('genre').values('genre').annotate(count=Count('genre'))

    total_genre_count = len(num_genre)
    genre_counts = {}
    keys = ['name','count']

    for i in range(total_genre_count):
        name = genre_names[i]
        count = genres[i]['count']
        values = [name,count]
        genre_counts[i] = dict(zip(keys, values))

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'genre_counts': genre_counts,
    }

    # render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AuthorDetailView, self).get_context_data(**kwargs)

        # Create any data and add it to the context
        books = Book.objects.all()
        context['books'] = books

        return context