from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from importacao import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('interface.urls')),
    path('importar/', views.importar_turma, name='upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)