from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
################################################################
from . import forms
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth import HASH_SESSION_KEY, authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
###########################################################
from django.core.mail import send_mail 
import random
###########################################################
from blog import models
from django.conf import settings
###########################################################
from django.views.generic import (TemplateView,ListView,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView)
###########################################################
from django.contrib.auth.mixins import LoginRequiredMixin    
########################################################### 
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger                             
# Create your views here.
###########################################################
def index(request):
    return render(request, 'base.html',{})
user=0
###########################################################
def otp_verify(request):
    otp = request.POST.get('otp')
    cotp = request.POST.get('cnf_otp')
    if otp == cotp:
        username = request.POST.get('username')
        #user = models.User.objects.get(username=username)
        user.save() 
        print('Account Created')
        return HttpResponseRedirect(reverse('blog:base'))
    else:
        return HttpResponse('Otp Not Matched')
###########################################################   
def user_register(request):
    user_form = forms.UserForm()
    dct = {'user': user_form}
    if request.method == 'POST':
        user_form = forms.UserForm(request.POST)
        if (user_form.is_valid()):
            ######################################
            otp = random.randint(a=1111, b=9999)
            mail = request.POST.get('email')
            send_mail('OTP Verification',
                        f'Here is Your OTP {otp} for Registration',
                        settings.EMAIL_HOST_USER,
                        [mail],
                        fail_silently=False,
                        )      
            ######################################
            global user
            user = user_form.save(commit=False)
            user.set_password(user.password)
            uname = request.POST.get('username')
            return render(request, 'register/otp_verify.html',{'otp':otp, 'username':uname})
            #---------------------------------------------------
        else:
            print(user_form.errors)
            return HttpResponse('<h1> Invalid Form </h1>')

    return render(request, 'register/reg.html',dct )
###########################################################
def user_login(request): 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        print(user)
        #----------------------------------------------------------
        if user:
            if user.is_active:
                login(request,user)
                
                request.session['username'] = username
                request.session['user_login'] = True
                # count = request.session.get('count',1) +  
                # request.session['count'] = count 
                #Set session as modified to force data updates/cookie to be saved.
                request.session.modified = True
                print('log in successful')  
                return HttpResponseRedirect(reverse('blog:base'))
            else:
                return HttpResponse('User not Active') 
        #----------------------------------------------------------
        else:
            print(":Log In Attempt Fail")
            return HttpResponse("<h1> Invalid Credentials </h1>")
        #----------------------------------------------------------
    else:
        return render(request, 'register/login.html') 
###########################################################
def user_logout(request):
    del request.session['username']
    del request.session['user_login'] 
    logout(request) 
    return HttpResponseRedirect(reverse('blog:base'))
###########################################################
def user_profile(request):

    form = forms.UserProfileForm(request.POST)    
    if request.method=='POST':
        prof_form = forms.UserProfileForm(request.POST, request.FILES)
        if prof_form.is_valid():
            username = request.session['username']
            user = models.User.objects.get(username=username)
            
            prof_model = prof_form.save(commit= False)
            if 'prof_pic' in request.FILES:
                prof_model.prof_pic = request.FILES['prof_pic']
            
            prof_model.user = user
            prof_model.save()
            return HttpResponse('<h1>Successfully Registered</h1>')

        else:
            print(form.errors)
            return HttpResponse('<h1>Form is not Valid</h1>')

    return render(request, 'register/profile.html', {'form':form})
##################################################################

@login_required
def special_fn(request):
    return HttpResponse('<h1>Special Request</h1>')
##################################################################
## class AboutView(TemplateView):
## template_name = 'about.html'

class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = '/blogs/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = forms.PostForm 
    model = models.Post 
    
    def form_valid(self, form):
        form = form.save(commit=False)
        print(form.author.username, '#########################')
        user = models.User.objects.get(username=self.request.session['username'])
        print(user.username, '#########################')
        if form.author == user:
            form = self.form_class(self.request.POST)
            return super().form_valid(form)

        else:
            return HttpResponse('<h1>Invalid Forms</h1>')

class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/blogs/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = forms.PostForm
    model = models.Post

class PostDetailView(DetailView):
    model = models.Post

class PostListView(ListView):
    model = models.Post
    def get_queryset(self):
        return models.Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class DraftListView(LoginRequiredMixin,ListView):
    login_url = '/blogs/login/'
    redirect_field_name = 'blog/post_list.html'
    model = models.Post
    paginate_by = 4
    

    def get_queryset(self):

        user = models.User.objects.get(username = self.request.session['username'])
        return models.Post.objects.filter(author = user,published_date__isnull=True).order_by('created_date')

    def get_context_data(self, **kwargs):
        context = super(DraftListView, self).get_context_data(**kwargs) 
        posts = self.model.objects.all()
        paginator = Paginator(list_exam, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            #file_exams = paginator.page(page)
            posts  = paginator.page(page)
        except PageNotAnInteger:
            #file_exams = paginator.page(1)
            posts = paginator.page(1)
        except EmptyPage:
            #file_exams = paginator.page(paginator.num_pages)
            posts = paginator.page(paginator.num_pages)
            
        #context['list_exams'] = file_exams
        context['posts'] = posts
        return context

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = models.Post
    success_url = reverse_lazy('blog:post_list')

##################################################
## Functions that require a pk match ##
##################################################

@login_required(login_url='/blogs/login/')
def post_publish(request, pk):
    post = get_object_or_404(models.Post, pk=pk)
    post.publish()
    return redirect('blog:post_detail', pk=pk)
##################################################

@login_required(login_url='/blogs/login/')
def add_comment_to_post(request, pk): 
    post = get_object_or_404(models.Post, pk=pk)
    if request.method == "POST": 
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = forms.CommentForm() 
    return render(request, 'blog/comment_form.html', {'form': form})

@login_required(login_url='/blogs/login/')
def comment_approve(request, pk): 
    comment = get_object_or_404(models.Comment, pk=pk)
    #comment.approve() 
    return redirect('blog:post_detail', pk=comment.post.pk) 

@login_required(login_url='/blogs/login/')
def comment_remove(request, pk): 
    comment = get_object_or_404(models.Comment, pk=pk) 
    post_pk = comment.post.pk 
    comment.delete() 
    return redirect('blog:post_detail', pk=post_pk)

#########################################################################