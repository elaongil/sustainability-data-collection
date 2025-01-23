from django.urls import path, include

urlpatterns = [
    path('cells/', include([
        path('wikipedia/', include('cells.wikipedia.urls')),
        path('', include('cells.sustainability.urls')),
    ])),
]
