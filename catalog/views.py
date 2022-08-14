import datetime

from django.db.models import Count
from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Book, Author, BookInstance, Genre
from catalog.forms import RenewBookForm


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


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)



class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    # initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    # initial = {'date_of_death': '11/06/2020'}

class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')