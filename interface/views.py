from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from .models import User,Task,UserProfile,Node
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.utils import timezone
# Create your views here.
import socket

def send_command(cmd='update'):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect (('10.50.70.173', 2727))
    try:
        client.send(cmd)
    except Exception:
        return 0
    finally:
        client.close()
        return 1
    
    
def index(request):
    context={}
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            # print "Yobaniy hui"
            login(request,user)
            return HttpResponseRedirect('/interface/')
            
        else:
            # print "Fuck you, hacker"
            # return render(request,'interface/auth.html',context)
            return HttpResponseRedirect("/")
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect("../interface")
        else:
            return render(request, 'interface/auth.html', context)
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/interface/')
    
@login_required
def interface(request):
    profile = UserProfile.objects.get(user_id=request.user.id)
    # print profile.score
    task_list = Task.objects.order_by('-date')
    task_list = Task.objects.filter(status__exact='in queue')
    # for task in task_list:
        # print task.date
    context = {'profile': profile,'task_list': task_list}
    # output = ", ".join([q.login for q in latest_question_list])
    return render(request,'interface/index.html',context)

@login_required
def add_task(request):
    profile = UserProfile.objects.get(user_id=request.user.id)
    print profile
    nodes = Node.objects.all()
    context = {'profile': profile,'nodes':nodes}
    if request.method == 'POST':
        user_id = request.user.id
        print request.user.username
        task = Task()
        task.user_id = request.user
        task.path = request.POST.get('task_path')
        task.options = request.POST.get('options')
        task.cpu = request.POST.get('cpu')
        task.ram = request.POST.get('ram')
        if request.POST.get('prime') == 'on':
            task.prime = True
        if request.POST.get('moretime') == 'on':
            task.moretime = True
        if request.POST.get('defnode') == 'on':
            task.defnode = True
        if task.defnode == 'on':
            task.node_id = request.POST.get('node_id')
        else:   
            task.node_id = '-1'
        task.date = timezone.now()
        task.save()
        send_command('update tasks')
    else:
        print request.user.username
    return render(request,'interface/add_form.html',context)
    
@login_required
def my_tasks(request):
    profile = UserProfile.objects.get(user_id=request.user.id)
    task_list = Task.objects.filter(user_id__exact=request.user.id)
    context = {'profile': profile,'task_list': task_list}
    # output = ", ".join([q.login for q in latest_question_list])
    return render(request,'interface/my_tasks.html',context)
    
@login_required
def nodes_info(request):
    profile = UserProfile.objects.get(user_id=request.user.id)
    nodes_list = Node.objects.all()
    context = {'profile': profile,'nodes_list': nodes_list}
    return render(request,'interface/nodes.html',context)
    # return render(request,'interface/my_tasks.html',context)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    