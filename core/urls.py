from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('memory/', views.memory_list_create, name='memory'),
    path('memory/<int:pk>/edit/', views.memory_update, name='memory_edit'),
    path('memory/<int:pk>/delete/', views.memory_delete, name='memory_delete'),
    path('documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('documents/', views.documents, name='documents'),
    path('message/', views.message, name='message'),
    path('family/', views.family, name='family'), 
    path('switch-settings/', views.switch_settings, name='switch_settings'),
    path('heir/', views.heir_portal, name='heir_portal'),
    path('heir/invite/<uuid:token>/', views.heir_claim, name='heir_claim'),
]