from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.LayoutsListView.as_view(), name='index'),
    path(r'<int:pk>/', views.LayoutView.as_view(), name='detail'),
    path(r'<int:pk>/init/', views.LayoutInitView.as_view(), name='init'),
    path(r'<int:pk>/update-from-current/', views.LayoutUpdateFromCurrentFileView.as_view(), name='update'),
    path(r'<int:pk>/edit/', views.LayoutRefreshEditTokenView.as_view(), name='edit'),
    path(r'precompute/', views.LayoutPrecomputeView.as_view(), name='precompute'),
    path(r'save-current-file/', views.SaveCurrentFileView.as_view(), name='save-current-file'),
]
