from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^interface/logout/$', views.user_logout, name='logout'),
    url(r'^interface/$', views.interface, name='interface'),
    url(r'^interface/add_task/$', views.add_task, name='add_task'),
    url(r'interface/my_tasks/$',views.my_tasks, name='my_tasks'),
    url(r'interface/nodes_info/$',views.nodes_info, name='nodes_info'),
]