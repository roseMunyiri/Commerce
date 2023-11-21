from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listings, Comments, Bids


def index(request):
    activeListings = Listings.objects.filter(isActive=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
         "listings": activeListings,
         "categories": categories

    })

def displayCategories(request):
    if request.method == "POST":
        formCategory = request.POST["category"]
        category = Category.objects.get(CategoryName=formCategory)

        print("form category:", formCategory)
        activeListings = Listings.objects.filter(isActive=True, category=category)
        categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": categories
        })
    else:
        # Handle the case where the form is not submitted
        categories = Category.objects.all()
        return render(request, "auctions/index.html", 
                      {"categories": categories})


def createListing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": categories
        })
    else:
        title = request.POST["title"]
        description= request.POST["description"]
        image = request.POST["image"]
        price = request.POST["price"]
        category_id = request.POST["category"]

        # Get current user
        currentUser = request.user

        # Get category data
        categoryData = Category.objects.get(id=category_id)
        bid = Bids.objects.create(bids=price, user=currentUser)

        bid.save()
        # Create new listing
        newListing = Listings.objects.create(
            title=title,
            description=description,
            imageurl=image,
            price=price,
            category=categoryData, 
            owner=currentUser
        )

        newListing.bid.add(bid)
        return HttpResponseRedirect(reverse("index"))
    
def addBid(request, id):
    return

def listing(request, id):
    listingDetails = Listings.objects.get(pk=id)
    allComments = Comments.objects.filter(listing=listingDetails)
    isInWatchlist = request.user in listingDetails.watchlist.all()
    return render(request, "auctions/listing.html", {
        "listing": listingDetails,
        "isInWatchlist": isInWatchlist,
        "allComments": allComments

    })

def removeWatchlist(request, id):
    listingData = Listings.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=[id]))

def addWatchlist(request, id):
    listingData = Listings.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect (reverse("listing", args=[id]))

def watchlist(request):
    currentUser =  request.user
    listings = currentUser.User.all()
    return render(request, "auctions/watchlist.html",{
        "listings": listings,
        "currentUser": currentUser
    })

def addComment(request, id):
    currentUser = request.user
    listingData = Listings.objects.get(pk=id)
    message = request.POST["comment"]
   
    newComment = Comments.objects.create(
        author = currentUser,
        listing = listingData,
        message = message
        )

    newComment.save()
    return HttpResponseRedirect (reverse("listing", args=[id]))
    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
