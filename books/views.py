import json
from datetime import datetime

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Book


def load_data():
    with open('fixtures/books.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data:
            name = item['fields']['name']
            author = item['fields']['author']
            pub_date_str = item['fields']['pub_date']
            pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d').date()
            book = Book(name=name, author=author, pub_date=pub_date)
            book.save()


def books_list(request, date=None):
    if not Book.objects.exists():
        load_data()

    book_list = Book.objects.all().order_by('pub_date')

    if date:
        book_list = book_list.filter(pub_date=date)

    paginator = Paginator(book_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if 'last_book_count' not in request.session:
        request.session['last_book_count'] = len(book_list)
    elif len(book_list) > request.session['last_book_count']:
        load_data()
        book_list = Book.objects.all().order_by('pub_date')
        paginator = Paginator(book_list, 10)
        page_obj = paginator.get_page(page_number)
        request.session['last_book_count'] = len(book_list)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'books/books_list.html', context)


def books_by_date(request, pub_date):
    template = 'books/books_list.html'
    book_list = Book.objects.filter(pub_date=pub_date).order_by('pub_date')
    paginator = Paginator(book_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'pub_date': pub_date,
    }
    return render(request, template, context)


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    previous_book = Book.objects.filter(pub_date__lt=book.pub_date).order_by('-pub_date').first()
    next_book = Book.objects.filter(pub_date__gt=book.pub_date).order_by('pub_date').first()

    context = {
        'book': book,
        'previous_book': previous_book,
        'next_book': next_book,
    }

    return render(request, 'books/book_detail.html', context)
