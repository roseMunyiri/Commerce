# auctions/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass 

class Category(models.Model):
    CategoryName = models.CharField(max_length=50)
    def __str__(self):
        return self.CategoryName
    
class Bids(models.Model):
    bids = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userBid")

    def __str__(self):
        return self.bids


class Listings(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    imageurl = models.CharField(max_length=1000)
    price = models.FloatField(default=0)
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, related_name="User")
    bid = models.ManyToManyField(Bids, related_name="bidListing" )


    def __str__(self):
        return self.title
    
class Comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="author")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, blank=True, null=True, related_name="listing")
    message = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.author} commented on {self.listing}"
    

