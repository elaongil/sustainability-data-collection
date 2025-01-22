from django.urls import path
from .views import WikipediaExtractorView

urlpatterns = [
    path('extract/', WikipediaExtractorView.as_view(), name='wikipedia-extract'),
]
