from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.utils import timezone
# Create your models here.
###############################################################################
class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete = models.CASCADE, 
                                      related_name='profile')
    
    prof_url = models.URLField()
    prof_pic = models.ImageField(upload_to='profile_pic/')
    #-------------------------------------------------------------- 
    def __str__(self):
        return self.user.username  

class Post(models.Model): 
    #--------------------------------------------------------------  
    author = models.ForeignKey(User, on_delete = models.CASCADE) 
    title = models.CharField(max_length=200) 
    text = models.TextField() 
    created_date = models.DateTimeField(default=timezone.now) 
    published_date = models.DateTimeField(blank=True, null=True) 
    #-------------------------------------------------------------- 
    def publish(self): 
        self.published_date = timezone.now() 
        self.save() 
    #-------------------------------------------------------------- 
    # def approve_comments(self): 
    #     return self.comments.filter(approved_comment=True) 
    # #-------------------------------------------------------------- 
    def get_absolute_url(self): 
        return reverse("blog:post_detail",kwargs={'pk':self.pk}) 
    #-------------------------------------------------------------- 
    def __str__(self): 
        return self.title 
    #--------------------------------------------------- 

########################################################   
class Comment(models.Model): 
    #---------------------------------------------------
    post = models.ForeignKey('blog.Post', related_name='comments', on_delete = models.CASCADE) 
    author = models.CharField(max_length=200) 
    text = models.TextField() 
    created_date = models.DateTimeField(default=timezone.now) 

    
    def get_absolute_url(self): 
        return reverse("blog:post_list") 
    #---------------------------------------------------
    def __str__(self): 
        return self.text 
    #---------------------------------------------------