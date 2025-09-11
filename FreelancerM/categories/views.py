from django.shortcuts import render, redirect
from .models import Category, Listing
from .forms import CategoryForm, ListingForm
from django.contrib.auth.decorators import login_required

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            return redirect('home')
    else:
        form = CategoryForm()
    return render(request, 'create_category.html', {'form': form})

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.posted_by = request.user
            listing.save()
            return redirect('home')
    else:
        form = ListingForm()
    return render(request, 'create_listing.html', {'form': form})

def category_listings(request, category_id):
    category = Category.objects.get(id=category_id)
    listings = category.listings.all()
    return render(request, 'category_listings.html', {'category': category, 'listings': listings})
