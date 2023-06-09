from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
from datetime import timedelta
import os

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True) #allow_unicode 한글 가능하게하는 코드

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories' #목록 이름 바꾸기

class News(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True) #allow_unicode 한글 가능하게하는 코드
    field = models.ManyToManyField(Category, blank=True, related_name='category')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/news/{self.slug}/'

    class Meta:
        verbose_name_plural = 'News' #목록 이름 바꾸기

class Post(models.Model):
    title = models.CharField(max_length=50)
    url = models.CharField(max_length=100, blank=True)
    writer = models.CharField(max_length=50, null=True, blank=True, default='작성자 없음')
    text_short = MarkdownxField() #models.TextField()
    text_middle = MarkdownxField()  # models.TextField()
    text_long = MarkdownxField()  # models.TextField()

    image = models.CharField(max_length=150, blank=True)
    # file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True, default='', null=True) #파일형식

    time = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, default='KYJ') #CASCADE 사용자의 탈퇴와 같이 글이 지워짐 SET_NULL NULL로 초기화 해줌(NULL=True 추가 필요)
    field = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(News, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'[{self.pk}] {self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    # def get_file_name(self): #파일 업로드
    #     return os.path.basename(self.file_upload.name)
    # def get_file_ext(self):
    #     return self.get_file_name().split('.')[-1]

    def get_content_short(self):
        return markdown(self.text_short)

    def get_content_middle(self):
        return markdown(self.text_middle)

    def get_content_long(self):
        return markdown(self.text_long)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/143/e3445497d896a175/svg/{self.author.email}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author}::{self.comment}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'

    def is_updated(self):
        return self.updated_at - self.created_at > timedelta(seconds=1)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/143/e3445497d896a175/svg/{self.author.email}'
