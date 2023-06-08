from django.db.models import Q
from django.shortcuts import render
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from .models import Post, Category, Comment, News
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CommentForm
from django.core.paginator import Paginator

def post(request):
    return render(request, 'index.html', {})

class PostList(ListView):
    model = Post
    ordering = '-time'  # 역순으로 정렬
    paginate_by = 7  # 페이지당 게시물 수

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(field=None).count()
        context['news1'] = News.objects.get(name='KBS')
        context['news2'] = News.objects.get(name='SBS')
        context['news3'] = News.objects.get(name='MBC')
        page = context['page_obj']
        paginator = page.paginator
        pagelist = paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=0)
        last_page = page.paginator.num_pages
        context['pagelist'] = pagelist
        context['last_page'] = last_page

        selected_content = self.request.GET.get('content', '')
        context['selected_content'] = selected_content

        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'text_short','text_middle', 'text_long', 'image', 'field', 'company'] #, 'file_upload'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'text_short', 'text_middle', 'text_long', 'image', 'field', 'company'] #  'file_upload',
    template_name ='blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(field=None).count()
        context['comment_form'] = CommentForm
        context['news1'] = News.objects.get(name='KBS')
        context['news2'] = News.objects.get(name='SBS')
        context['news3'] = News.objects.get(name='MBC')
        return context

def category_page(request, slug):

    if slug == 'no_category':
        field = '미분류'
        post_list = Post.objects.filter(field=None).order_by('-time')
    else:
        field = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(field=field).order_by('-time')

    selected_content = request.GET.get('content', '')

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(field=None).count(),
            'category': field,
            'news1': News.objects.get(name='KBS'),
            'news2': News.objects.get(name='SBS'),
            'news3': News.objects.get(name='MBC'),
            'selected_content': selected_content,
        }
    )

def news_page(request, slug):
    if slug == 'no_news':
        company = '미분류'
        post_list = Post.objects.filter(company=None).order_by('-time')
    else:
        company = News.objects.get(slug=slug)
        post_list = Post.objects.filter(company=company).order_by('-time')

    selected_content = request.GET.get('content', '')

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(field=None).count(),
            'news': company,
            'news1': News.objects.get(name='KBS'),
            'news2': News.objects.get(name='SBS'),
            'news3': News.objects.get(name='MBC'),
            'selected_content': selected_content,
        }
    )

def news_category_page(request, slug1, slug2):
    if slug1 == 'no_news':
        company = '미분류'
        news_list = Post.objects.filter(company=None).order_by('-time')
    else:
        company = News.objects.get(slug=slug1)
        news_list = Post.objects.filter(company=company).order_by('-time')

    if slug2 == 'no_category':
        field = '미분류'
        post_list = news_list.filter(field=None).order_by('-id')
    else:
        field = Category.objects.get(slug=slug2)
        post_list = news_list.filter(field=field).order_by('-id')

    selected_content = request.GET.get('content', '')

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(field=None).count(),
            'category': field,
            'news': company,
            'news1': News.objects.get(name='KBS'),
            'news2': News.objects.get(name='SBS'),
            'news3': News.objects.get(name='MBC'),
            'selected_content': selected_content,
        }
    )

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid(): #is_valid() 요소가 적합한 경우에 1
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        return redirect(post.get_absolute_url())

    else:
        raise PermissionError

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm


    def dispatch(self, request, *args, **kwargs): #사용자 확인
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

from django.db.models import Q

from django.db.models import Q

class PostSearch(PostList):
    paginate_by = 7

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.kwargs['q']
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(text_long__icontains=q) |
                Q(text_middle__icontains=q) |
                Q(text_short__icontains=q)
            )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.kwargs['q']
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['search_info'] = f'Search: {q} ({queryset.count()})'
        context['page_obj'] = page_obj

        selected_content = self.request.GET.get('content', '')  # 선택한 내용 가져오기
        context['selected_content'] = selected_content  # 선택한 내용 전달

        return context


# class Sign_up(DetailView):
#     model = Post
#     template_name = 'blog/sign_up.html'

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