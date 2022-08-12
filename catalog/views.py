from django.db.models import Count
from django.shortcuts import render
from django.views import generic
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin


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


    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'genre_counts': genre_counts,
        'num_visits': num_visits,
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


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllLoanedBooksListView(LoginRequiredMixin,generic.ListView):

    model = BookInstance
    template_name ='catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')