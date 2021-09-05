from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class URLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_another = User.objects.create_user(username='another')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='text',
        )
        cls.guest_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_another)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            f'/group/{URLTest.group.slug}/': 'group_list.html',
            f'/profile/{URLTest.user.username}/': 'posts/profile.html',
            f'/posts/{URLTest.post.id}/': 'posts/post_detail.html',
            f'/posts/{URLTest.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_create_post_url_redirect_anonymous_on_admin_login(self):
        """URL-адрес перенаправляет незарегистрированного пользователя."""
        adresses_redirect_urls = {
            f'/posts/{URLTest.post.id}/edit/':
            f'/auth/login/?next=/posts/{URLTest.post.id}/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for adress, url in adresses_redirect_urls.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(
                    response, url
                )

    def test_create_post_url_redirect_not_author(self):
        """URL-адрес перенаправляет, если пользователь не автор."""
        response = self.authorized_client.get(
            f'/posts/{URLTest.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{URLTest.post.id}/')

    def test_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        adresses = [
            '/',
            f'/group/{URLTest.group.slug}/',
            f'/profile/{URLTest.user.username}/',
            f'/posts/{URLTest.post.id}/',
        ]
        for adress in adresses:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_any(self):
        """Страница доступна любому авторизованному пользователю."""
        adresses = [
            '/',
            f'/group/{URLTest.group.slug}/',
            f'/profile/{URLTest.user.username}/',
            f'/posts/{URLTest.post.id}/',
            '/create/',
        ]
        for adress in adresses:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_authorized(self):
        """Страница доступна автору."""
        adresses = [
            '/',
            f'/group/{URLTest.group.slug}/',
            f'/profile/{URLTest.user.username}/',
            f'/posts/{URLTest.post.id}/',
            f'/posts/{URLTest.post.id}/edit/',
            '/create/',
        ]
        for adress in adresses:
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def unexisting_page_does_not_exist(self):
        """Несуществующая страница выдает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
