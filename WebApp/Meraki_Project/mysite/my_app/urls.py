from django.conf.urls import url
from my_app import views

app_name='my_app'

urlpatterns=[
    url(r'^user_login/$',views.user_login,name='user_login'),
    # http://127.0.0.1:8000/logs
    # http://127.0.0.1:8000/logs/
    url(r'^logs/$',views.logs,name='logs'),
]
