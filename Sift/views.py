from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from Sift.models import Poll,Choice


def details(request, poll_id):
    question = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'details.html', {'question': question})


def results(request, poll_id):
    question = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'results.html', {'question': question})


def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'details.html', {
            'question': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))


def index(request):
    latest_question_list = Poll.objects.all
    context = {'latest_question_list': latest_question_list}
    return render(request, 'index.html', context)


def general(request):
    return render(request, 'general_analytics.html')