from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('search/', views.product_search, name='product_search'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('review/add/<str:order_id>/<int:product_id>/', views.add_review, name='add_review'),
]
