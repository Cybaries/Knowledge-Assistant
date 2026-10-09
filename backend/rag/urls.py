from django.urls import path

from rag.views import QueryView

app_name = "rag"

urlpatterns = [
    path("query/", QueryView.as_view(), name="query"),
]
