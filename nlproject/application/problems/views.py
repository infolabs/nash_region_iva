from datetime import datetime

from django.views.generic.edit import FormView
from django.http import JsonResponse

from problems.forms import ProblemClassifierForm
from problems.classifier import Classifier

classifier = Classifier()

print('Loading problems...')
classifier.load_problems()

print('Processing problems...')
classifier.process_problems()


def classify(request):
    text = request.GET.get('text')
    suggestions = classifier.classify(text)
    data = {'suggestions': suggestions[:5]}
    return JsonResponse(data)


class ProblemClassifierView(FormView):
    form_class = ProblemClassifierForm
    template_name = 'problems/classify.html'
    success_url = '/'
