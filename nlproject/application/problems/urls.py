from django.urls import path

from problems.views import ProblemClassifierView
from problems.views import classify


urlpatterns = [
    path('', ProblemClassifierView.as_view()),
    path('ajax/classify', classify, name='classify'),
]
