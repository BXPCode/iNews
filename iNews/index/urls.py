from . import views
from django.urls import path

urlpatterns = [
    path('', views.index_view),
    path('content', views.content_view),
    path('cate', views.cate_view),
    path('voteChange', views.vote_change_view),
]
