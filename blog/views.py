from django.db.models import Q
from django.shortcuts import render
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from .models import Post, Category, Tag, Comment, News
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CommentForm

def post(request):
    return render(request, 'index.html', {})

class PostList(ListView):
    model = Post
    ordering = '-pk' #역순으로
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['news1'] = News.objects.get(id=1)
        context['news2'] = News.objects.get(id=2)
        context['news3'] = News.objects.get(id=3)
        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'news']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip() #strip(앞뒤 공백 제거)
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t) #tag=태그 인자, is_tag_created= 태그가 새로 생성된건지 True/False
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'news']
    template_name ='blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_defaults'] = '; '.join(tags_str_list)
        return context

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear() #연결을 삭제 / deleate는 db에서 삭제

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()  # strip(앞뒤 공백 제거)
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(
                    name=t)  # tag=태그 인자, is_tag_created= 태그가 새로 생성된건지 True/False
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        context['news1'] = News.objects.get(id=1)
        context['news2'] = News.objects.get(id=2)
        context['news3'] = News.objects.get(id=3)
        return context

def category_page(request, slug):

    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
            'news1': News.objects.get(id=1),
            'news2': News.objects.get(id=2),
            'news3': News.objects.get(id=3),
        }
    )

def news_page(request, slug):
    if slug == 'no_news':
        news = '미분류'
        post_list = Post.objects.filter(news=None)
    else:
        news = News.objects.get(slug=slug)
        post_list = Post.objects.filter(news=news)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'news': news,
            'news1': News.objects.get(id=1),
            'news2': News.objects.get(id=2),
            'news3': News.objects.get(id=3),
        }
    )

def news_category_page(request, slug1, slug2):
    if slug1 == 'no_news':
        news = '미분류'
        news_list = Post.objects.filter(news=None)
    else:
        news = News.objects.get(slug=slug1)
        news_list = Post.objects.filter(news=news)

    if slug2 == 'no_category':
        category = '미분류'
        post_list = news_list.filter(category=None)
    else:
        category = Category.objects.get(slug=slug2)
        post_list = news_list.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
            'news': news,
            'news1': News.objects.get(id=1),
            'news2': News.objects.get(id=2),
            'news3': News.objects.get(id=3),
        }
    )

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'tag': tag,
            'news1': News.objects.get(id=1),
            'news2': News.objects.get(id=2),
            'news3': News.objects.get(id=3),
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

class PostSearch(PostList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q'] #class에서 인자를 받는법
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q) #q를 포함하는 카테고리를 가져온다.
        ).distinct() #중복방지
        return post_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'

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