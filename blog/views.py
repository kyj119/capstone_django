from django.shortcuts import render
from .models import Post

def index(request):
    posts = Post.objects.all().order_by('pk') #order_by 받는 순서

    return render(
        request,
        'blog/index.html',
        {
          'posts': posts,
        }
    )