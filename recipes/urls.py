from django.urls import path
# from recipes.views import JoinFormView
from . import views
# from . import views, settings
# from django.contrib.staticfiles.urls import static
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
 
 
# urlpatterns += staticfiles_urlpatterns()
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = 'recipes'
urlpatterns = [
    path('search/', views.check, name='check'),
    path('create/', views.ajax, name='ajax'),
    path('home/', views.test, name='test'),
	path('<int:id>/', views.recipe, name='recipe'),
    # path(r'^signup/$', views.SignUpView.as_view(),
]