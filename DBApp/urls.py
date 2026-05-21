# DBApp/urls.py

from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('shops/', views.shops, name='shops'),
    path('view-details/<int:id>/', views.view_details, name='view_details'),
    path('add-invoice/<int:id>/', views.add_invoice, name='add_invoice'),
    path('edit-invoice/<int:id>/', views.edit_invoice, name='edit_invoice'),
    path('delete-invoice/<int:id>/', views.delete_invoice, name='delete_invoice'),
    path('download-invoice/<int:id>/', views.download_invoice, name='download_invoice'),
    path('', views.home, name='home'),
    path('shops-auth/', views.shops_auth, name='shops_auth'),
    path('shops/', views.shops, name='shops'),
    path('invoice_success/<int:id>/',views.invoice_success,name='invoice_success'),
]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)