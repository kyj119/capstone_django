from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
    def test_post_list(self):
        self.assertEqual(2,2)
        # 1.1 post_list를 연다.
        response = self.client.get('/blog/')
        # 1.2 정상적으로 load되는지 확인한다.
        self.assertEqual(response.status_code, 200)
        # 1.3 페이지의 타이틀에 Blog라는 문구가 있다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn('Blog', soup.title.text)
        # 1.4 NavBar가 있다.
        navbar = soup.nav
        # 1.5 Blog, About me의 배너가 있다.
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        # 2.1 게시물이 하나도 없을때
        self.assertEqual(Post.objects.count(), 0)
        # 2.2 메인 영역에 "아직 게시물이 없습니다." 라는 문구가 나온다.
        main_area = soup.find('div', id='main_area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

        # 3.1 만약 게시물이 2개 있다면.
        post_001 = Post.objects.create(
            title='첫번째 포스트 입니다.',
            content='Hello, world We are the World.',
        )
        post_002 = Post.objects.create(
            title='두번째 포스트 입니다.',
            content = '1등이 전부는 아니잖아요.',
        )
        self.assertEqual(Post.objects.count(), 2)
        # 3.2 포스트 목록 페이지를 새로 고침했을때
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        # 3.3 메인 영역에 포스트 2개의 타이틀이 존재한다.
        main_area = soup.find('div', id='main_area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        # 3.4 "아직 게시물이 없습니다" 라는 문구 제거.
        self.assertNotIn('아직 게시물이 없습니다',main_area)