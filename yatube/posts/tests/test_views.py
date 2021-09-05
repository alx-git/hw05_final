import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PagesTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.another_user_1 = User.objects.create_user(
            username='another_auth_1'
        )
        cls.another_user_2 = User.objects.create_user(
            username='another_auth_2'
        )
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='text',
            image=uploaded
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another_authorized_client_1 = Client()
        cls.another_authorized_client_1.force_login(cls.another_user_1)
        cls.another_authorized_client_2 = Client()
        cls.another_authorized_client_2.force_login(cls.another_user_2)

    def test_page_uses_correct_template(self):
        """URL-адрес использует корректный шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
            'group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def check_context_for_paginator(self, response):
        self.assertEqual(
            response.context.get('page_obj').object_list[0].text,
            PagesTests.post.text
        )
        self.assertEqual(
            response.context.get('page_obj').object_list[0].author.username,
            PagesTests.post.author.username
        )
        self.assertEqual(
            response.context.get('page_obj').object_list[0].group.title,
            PagesTests.post.group.title
        )
        self.assertEqual(
            response.context.get('page_obj').object_list[0].image,
            PagesTests.post.image
        )

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        PagesTests.check_context_for_paginator(self, response)

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}
        ))
        PagesTests.check_context_for_paginator(self, response)
        self.assertEqual(
            response.context.get('group').title,
            PagesTests.group.title
        )

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        PagesTests.check_context_for_paginator(self, response)
        self.assertEqual(
            response.context.get('author').username,
            PagesTests.user.username
        )
        self.assertEqual(response.context.get('post_number'), 1)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(
            response.context.get('post').text,
            PagesTests.post.text
        )
        self.assertEqual(
            response.context.get('post').author.username,
            PagesTests.post.author.username
        )
        self.assertEqual(
            response.context.get('post').group.title,
            PagesTests.post.group.title
        )
        self.assertEqual(
            response.context.get('post').image,
            PagesTests.post.image
        )
        self.assertEqual(response.context.get('post_number'), 1)
        self.assertEqual(
            response.context.get('post_first30'),
            PagesTests.post.text[0:29]
        )
        self.assertEqual(
            response.context.get('post_group').title,
            PagesTests.post.group.title
        )
        self.assertEqual(
            response.context.get('post_group').slug,
            PagesTests.post.group.slug
        )
        self.assertEqual(
            response.context.get('post_group').description,
            'description'
        )
        self.assertEqual(
            response.context.get('user').username,
            PagesTests.user.username
        )

    def check_forms(self, response):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_pages_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        PagesTests.check_forms(self, response)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        ))
        PagesTests.check_forms(self, response)
        self.assertEqual(
            response.context.get('post').text,
            PagesTests.post.text
        )
        self.assertEqual(
            response.context.get('post').author.username,
            PagesTests.post.author.username
        )
        self.assertEqual(
            response.context.get('post').group.title,
            PagesTests.post.group.title
        )
        self.assertEqual(response.context.get('is_edit'), True)

    def test_profile_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей."""
        self.another_authorized_client_1.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Follow.objects.count(), 1)
        self.assertTrue(Follow.objects.filter(
            user=self.another_user_1,
            author=self.user
        ).exists())

    def test_profile_unfollow(self):
        """Авторизованный пользователь может отписываться от других
        пользователей."""
        self.another_authorized_client_1.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))
        self.another_authorized_client_1.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Follow.objects.count(), 0)

    def test_profile_follow_page(self):
        """Новая запись пользователя появляется в ленте тех, кто на
        него подписан и не появляется в ленте тех, кто не подписан."""
        self.another_authorized_client_1.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))
        response_1 = self.another_authorized_client_1.get(reverse(
            'posts:follow_index'
        ))
        self.assertIn(
            PagesTests.post,
            response_1.context.get('page_obj').object_list
        )
        response_2 = self.another_authorized_client_2.get(reverse(
            'posts:follow_index'
        ))
        self.assertNotIn(
            PagesTests.post,
            response_2.context.get('page_obj').object_list
        )


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='text',
            )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_first_page_contains_ten_records(self):
        """Проверка первой страницы Paginator."""
        url_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for url in url_list:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка второй страницы Paginator."""
        url_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for url in url_list:
            with self.subTest(value=url):
                response = self.authorized_client.get((url) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class PostGroupTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group_1 = Group.objects.create(
            title='title_1',
            slug='slug_1',
            description='description_1',
        )
        cls.post_1 = Post.objects.create(
            author=cls.user,
            group=cls.group_1,
            text='text_1',
        )
        cls.group_2 = Group.objects.create(
            title='title_2',
            slug='slug_2',
            description='description_2',
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            group=cls.group_2,
            text='text_2',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_posts_appear_on_pages(self):
        """Пост с группой появляется на страницах."""
        url_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group_1.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for url in url_list:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                self.assertIn(
                    self.post_1,
                    response.context.get('page_obj').object_list
                )

    def test_posts_does_not_appear_not_relevant_group(self):
        """Пост не попадает в группу для которой не предназначен."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group_2.slug}
        ))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(
            response.context.get('page_obj').object_list[0].text,
            PostGroupTests.post_2.text
        )
