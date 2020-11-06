from django.core.cache import cache, caches
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


class ModelsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="User11",
            email="User@11.11",
            password="qwe",
        )
        self.group = Group.objects.create(
            title='group',
            slug='group_slug',
            description='description')
        self.group2 = Group.objects.create(
            title='group2',
            slug='group_slug2',
            description='description2')
        self.client.force_login(self.user)
        self.anonym = Client()
        self.post = Post.objects.create(
            text="Test post",
            author=self.user,
            group=self.group,
        )
        self.POST_EDITED_TEXT = "Edited post"
        self.POST_NEW_TEXT = "New post"
        self.INDEX = reverse('index')
        self.POST_GROUP = reverse(
            'group',
            args=[self.group.slug]
        )
        self.POST_NEW = reverse('post_new')
        self.POST_DETAIL = reverse(
            'post_detail',
            args=[self.user.username,
                  self.post.id]
        )
        self.PROFILE = reverse(
            'profile',
            args=[self.user.username]
        )
        self.POST_EDIT = reverse(
            'post_edit',
            args=[self.user.username,
                  self.post.id]
        )
        self.URLS = (
            self.INDEX,
            self.PROFILE,
            self.POST_DETAIL,
            self.POST_GROUP,
        )

    def post_atribute_equal(self, tested_post, test_text, test_group,
                            test_author):
        self.assertEqual(
            tested_post.text,
            test_text,
            msg='Текст поста не соответствует'
        )
        self.assertEqual(
            tested_post.group,
            test_group,
            msg='Группа поста не соответствует'
        )
        self.assertEqual(
            tested_post.author,
            test_author,
            msg='Автор поста не соответствует'
        )

    def test_profile_exist(self):
        """
        После регистрации пользователя создается его
        персональная cтраница (profile)
        """
        response = self.client.get(self.PROFILE)
        self.assertEqual(
            response.status_code,
            200,
            msg='Профиль не найден'
        )

    def test_client_post(self):
        """
        Авторизованный пользователь может опубликовать пост (new)
        """
        cache.clear()
        post_count = Post.objects.count()

        response = self.client.post(
            self.POST_NEW,
            {
                'text': self.POST_NEW_TEXT,
                'group': self.group.id,
            },
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            msg='Пост не добавлен в базу'
        )
        post = response.context['page'][0]
        self.post_atribute_equal(
            post,
            self.POST_NEW_TEXT,
            self.group,
            self.user
        )

    def test_redirect_post(self):
        """
        Неавторизованный посетитель не может опубликовать пост
        (его редиректит на страницу входа)
        """
        post_count = Post.objects.count()

        response = self.anonym.post(
            self.POST_NEW,
            {
                'text': self.POST_NEW_TEXT,
                'group': self.group.id,
            },
            follow=False
        )

        self.assertEqual(
            response.status_code,
            302,
            msg='Нет редиректа'
        )
        self.assertEqual(
            Post.objects.count(),
            post_count,
            msg='Пост создается у неавторизированного пользователя'
        )

    def test_post_in_pages(self):
        """
        После публикации поста новая запись появляется на главной странице сайта (index),
        на персональной странице пользователя (profile),
        и на отдельной странице поста (post)
        """
        cache.clear()
        for url in self.URLS:
            with self.subTest(url=url, msg=f'Запись не найдена'
                                           f' на странице'):
                response = self.client.get(url)
                paginator = response.context.get('paginator')
                if paginator is not None:
                    post = response.context['page'][0]
                else:
                    post = response.context['post']
                self.assertEqual(
                    post,
                    self.post,
                    msg='Пост не соотвествует заданному'
                )

    def test_edit(self):
        """
        Авторизованный пользователь может отредактировать свой пост,
        после этого содержимое поста изменится на всех связанных страницах.
        """
        response = self.client.post(
            self.POST_EDIT,
            {
                'text': self.POST_EDITED_TEXT,
                'group': self.group2.id,
            }, follow=True
        )

        self.assertEqual(
            response.status_code,
            200,
            msg='Сервер вернул неожиданный ответ'
        )
        self.post.refresh_from_db()
        post = response.context['post']
        self.post_atribute_equal(
            post,
            self.POST_EDITED_TEXT,
            self.group2,
            self.user
        )

    def test404(self):
        """
        возвращает ли сервер код 404, если страница не найдена.
        """
        response = self.client.get('/test/')
        self.assertEqual(
            response.status_code,
            404,
            msg='Сервер вернул неожиданный ответ'
        )

    def test_non_image_upload(self):
        with open('media/posts/new.txt', 'rb') as img:
            post = self.client.post(
                self.POST_EDIT,
                {
                    'author': self.user,
                    'text': 'post with image',
                    'image': img
                }
            )
            response = self.client.get(self.POST_DETAIL)
            # print(response.content)
            self.assertNotContains(
                response,
                '<img class="card-img"',

            )

    def test_image_in_post(self):
        """"""
        cache.clear()
        with open('media/posts/winter.jpg', 'rb') as img:
            self.client.post(
                self.POST_EDIT,
                {
                    'author': self.user,
                    'text': 'post with image',
                    'group': self.group.id,
                    'image': img
                }
            )
            for url in self.URLS:
                with self.subTest(url=url, msg=f'Запись не найдена'
                                               f' на странице'):
                    response = self.client.get(url)
                    # print(response.content)
                    self.assertContains(
                        response,
                        '<img class="card-img"',
                    )

    def test_cache(self):
        post_count = Post.objects.count()
        self.client.get(self.INDEX)
        response = self.client.post(
            self.POST_NEW,
            {
                'text': 'new',
                'group': self.group.id,
            },
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            msg='Пост не добавлен в базу'
        )

        with self.assertRaises(TypeError):
            post = response.context['page'][0]
        cache.clear()
        index = self.client.get(self.INDEX)
        self.assertEqual(
            index.context['page'][0].text,
            'new',
            msg='Пост не появился после очитски кэша'
        )
