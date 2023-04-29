from django.shortcuts import render
from .models import Post
from django.views.generic import ListView, DetailView

class PostList(ListView):
    model = Post
    # ordering = '-pk' 순서 역순으로

class PostDetail(DetailView):
    model = Post

# def index(request):
#     posts = Post.objects.all().order_by('pk') #order_by 받는 순서
#
#     return render(
#         request,
#         'blog/post_list.html',
#         {
#           'posts': posts,
#         }
#     )

# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'post': post,
#         }
#     )