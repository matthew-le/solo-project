from django.urls import path
from . import views

urlpatterns = [
    path('', views.store),
    path('register', views.registerPage),
    path('login', views.loginPage),
    path('logout', views.logoutUser),
    path('cart', views.cart),
    path('checkout', views.checkout),
    path('update_item', views.updateItem),
    path('process_order', views.processOrder),
    path('<int:product_id>/like', views.like),
    path('<int:product_id>/unlike', views.unlike),
    path('account', views.customerAccount)
]