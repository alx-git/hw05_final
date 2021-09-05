from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='text'
        )
        cls.client = Client()

    def test_page_uses_correct_template(self):
        """Кэширование страницы работает."""
        response_1 = self.client.get(reverse('posts:index'))
        CacheTests.post.delete()
        response_2 = self.client.get(reverse('posts:index'))
        self.assertEqual(
            response_1.content,
            response_2.content,
        )
        cache.clear()
        response_3 = self.client.get(reverse('posts:index'))
        self.assertNotEqual(
            response_1.content,
            response_3.content,
        )
