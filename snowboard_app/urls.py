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
    path('<int:product_id>/favorite', views.favorite),
    path('<int:product_id>/unfavorite', views.unfavorite),
    path('<int:comment_id>/like', views.like),
    path('<int:comment_id/unlike', views.unlike),
    path('account', views.customerAccount),
    path('account/update', views.update_user),
    path('blog', views.blog),
    path('blog/post_comment', views.post_comment),
]