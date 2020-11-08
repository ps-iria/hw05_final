from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User, Follow, Comment


class ModelsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="User11",
            email="User@11.11",
            password="qwe",
        )
        self.user2 = User.objects.create_user(
            username="User22",
            email="User@22.22",
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
        self.PROFILE2 = reverse(
            'profile',
            args=[self.user2.username]
        )
        self.POST_EDIT = reverse(
            'post_edit',
            args=[self.user.username,
                  self.post.id]
        )
        self.PROFILE_FOLLOW = reverse(
            'profile_follow',
            args=[self.user.username]
        )
        self.PROFILE_UNFOLLOW = reverse(
            'profile_unfollow',
            args=[self.user.username]
        )
        self.PROFILE_FOLLOW2 = reverse(
            'profile_follow',
            args=[self.user2.username]
        )
        self.PROFILE_UNFOLLOW2 = reverse(
            'profile_unfollow',
            args=[self.user2.username]
        )
        self.FOLLOW = reverse(
            'follow_index',
        )
        self.COMMENT = reverse(
            'add_comment',
            args=[self.user.username,
                  self.post.id]
        )
        self.LOGIN = reverse(
            'login',
        )
        self.image = self.create_image()
        self.file = self.create_file()

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

    def create_image(self):
        image = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21'
            b'\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00'
            b'\x01\x00\x00\x02\x02\x4c\x01\x00\x3b')
        file = SimpleUploadedFile(
            name='test.jpg',
            content=image,
            content_type='image/jpg',
        )
        return file

    def create_file(self):
        file = SimpleUploadedFile(
            name='test.txt',
            content=b'text '
                    b'text',
            content_type='text/plain'
        )
        return file

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
        """
        Тест проверяющий загрузку изображения
        """
        response = self.client.post(
            self.POST_EDIT,
            {
                'author': self.user,
                'text': 'post with image',
                'group': self.group.id,
                'image': self.file
            }
        )
        self.assertContains(
            response,
            'Загрузите правильное изображение. Файл, который вы загрузили, '
            'поврежден или не является изображением.',
        )

    def test_image_in_post(self):
        """
        Тест проверяющий что загруженный файл является изображением
        """
        cache.clear()
        self.client.post(
            self.POST_EDIT,
            {
                'author': self.user,
                'text': 'post with image',
                'group': self.group.id,
                'image': self.image
            }
        )
        for url in self.URLS:
            with self.subTest(url=url, msg=f'Изображение не найдено'
                                           f' на странице'):
                response = self.client.get(url)
                self.assertContains(
                    response,
                    '<img',
                )

    def test_cache(self):
        """
        Тест, который проверяет работу кэша
        """
        self.client.get(self.INDEX)
        post = Post.objects.create(
            text="new",
            author=self.user,
            group=self.group,
        )
        response = self.client.get(self.INDEX)
        self.assertNotContains(
            response,
            post,
        )
        cache.clear()
        index = self.client.get(self.INDEX)
        self.assertEqual(
            index.context['page'][0],
            post,
            msg='Пост не появился после очитски кэша'
        )

    def test_follow(self):
        """
        Авторизованный пользователь может подписываться
        на других пользователей.
        """
        response = self.client.get(self.PROFILE2)
        self.assertContains(
            response,
            self.FOLLOW,
            msg_prefix='На странице нет кнопки "Подписаться"')

    def test_unfollow(self):
        """
        Авторизованный пользователь может удалять других пользователей
        из подписок.
        """
        response = self.client.get(
            self.PROFILE_FOLLOW2,
            follow=True
        )
        self.assertContains(
            response,
            self.PROFILE_UNFOLLOW2,
            msg_prefix='На странице нет кнопки "Отписаться"')
        self.assertTrue(
            Follow.objects.filter(user=self.user,
                                  author=self.user2).exists(),
            "Запись не добавленна в базу")

    def test_follow_posts(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан на него.
        """
        Follow.objects.create(
            user=self.user,
            author=self.user2
        )
        post_user2 = Post.objects.create(
            text="Test user2 post",
            author=self.user2,
            group=self.group2,
        )
        post_user = Post.objects.create(
            text="Test user post",
            author=self.user,
            group=self.group2,
        )
        response = self.client.get(self.FOLLOW)
        self.assertIn(
            post_user2, response.context['page'],
            "Посты из подписок не появляются в ленте Избранных")
        self.assertNotIn(
            post_user, response.context['page'],
            "Посты не из подписок появляются в ленте Избранных")

    def test_anonym_comment(self):
        """
        Неавторизированный пользователь не может комментировать посты.
        """
        response = self.anonym.post(
            self.COMMENT,
            {
                'text': 'test comment'
            },
            follow=True
        )
        self.assertFalse(
            Comment.objects.filter(post=self.post,
                                   text='test comment').exists(),
            'Комментарий добавился в базу')
        self.assertRedirects(
            response,
            '%s?next=%s' % (self.LOGIN, self.COMMENT),
            msg_prefix='Анонимный пользователь не перенаправлен '
                       'на страницу логина')

    def test_user_comment(self):
        """
        Авторизированный пользователь может комментировать посты.
        """
        response = self.client.post(
            self.COMMENT,
            {
                'text': 'test comment'
            },
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(post=self.post,
                                   text='test comment').exists(),
            'Комментарий не добавился в базу')
        self.assertRedirects(
            response,
            self.POST_DETAIL,
            msg_prefix='После комментария пользователь не перенаправлен'
                       'на страницу поста')
        self.assertEqual(
            response.context['comments'][0].text,
            'test comment',
            'Комментарий не найден на странице'
        )
