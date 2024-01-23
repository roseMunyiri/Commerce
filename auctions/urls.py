from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.createListing, name="create"),
    path("display", views.displayCategories, name="display"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("remove/<int:id>", views.removeWatchlist, name="remove"),
    path("add/<int:id>", views.addWatchlist, name="add"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment/<int:id>", views.addComment, name="comment"),
    path("addBid/<int:id>", views.addBid, name="addBid"),
    path('chat/<int:id>/', views.chat, name='chat'),



]
