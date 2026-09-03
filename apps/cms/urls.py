from django.urls import path

from .media_views import CmsMediaListView, CmsMediaUploadView
from .views import CmsContentView, PublishedCmsView

app_name = "cms"

urlpatterns = [
    path("cms/", PublishedCmsView.as_view(), name="published"),
    path("cms/content/", CmsContentView.as_view(), name="content"),
    path("cms/media/", CmsMediaListView.as_view(), name="media-list"),
    path("cms/media/upload/", CmsMediaUploadView.as_view(), name="media-upload"),
]
