from django.urls import path, include

urlpatterns = [
    path('cells/', include([
        path('wikipedia/', include('cells.wikipedia.urls')),
        # Add other cell URLs here
    ])),
]
