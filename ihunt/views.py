from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout, get_user
from ihunt.models import Clue, Guess, Event

def render_with_context(request, *args, **kwargs):
    render_context = RequestContext(request)
    return render_to_response(*args, context_instance=render_context, **kwargs)

def dumb_template(template_name):
    """ Returns a view function that renders the template """
    def view_func(request):
        return render_with_context(request, template_name)
    return view_func

def with_event(f):
    """ Returns a wed function that receives an `event` kwarg """
    class NoCurrentEventError(Exception):
        pass
    def view_func(request, event_id=None, *args, **kwargs):
        event = None

        if event_id is not None:
            event = get_object_or_404(Event, pk=event_id)
        else:
            event = get_object_or_404(Event, current=True)

        return f(request, event=event, *args, **kwargs)
    return view_func

index = dumb_template('index.html.tmpl')
help = dumb_template('help.html.tmpl')
faq = dumb_template('faq.html.tmpl')

@with_event
def test_view(request, event=None):
    return render_with_context(
        request, 
        'test.html.tmpl',
        {'event': event}
    )

def hunt(request):
    clue = Clue.objects.all()[0]
    if request.method == 'GET':
        return render_with_context(
            request,
            "hunt.html.tmpl",
            {'clue': clue}
        )
    elif request.method == 'POST':
        given_answer = request.POST['answer']
        guess = Guess(
            guess=given_answer,
            for_clue=clue,
            by = get_user(request).profile
        )
        guess.save()
        matching_answers = clue.answer_set.filter(answer__iexact=given_answer).count()
        return render_with_context(
            request,
            "hunt.html.tmpl",
            {'clue': clue}
        )

def login_view(request):
    if request.method == 'GET':
        return render_with_context(request, "login.html.tmpl")
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('index')
        return render_with_context(request, "login.html.tmpl", {'flash': 'Invalid login'})

def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('index')
