from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_models_have_correct_object_names_post(self):
        """Значение поля __str__ правильно отображает в объекте Post"""
        post = ModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(str(post), expected_object_name)

    def test_models_have_correct_object_names_group(self):
        """Значение поля __str__ правильно отображает в объекте Group"""
        group = ModelTest.group
        expected_object_name = group.title
        self.assertEqual(str(group), expected_object_name)

    def test_models_have_correct_verbose_names(self):
        """Проверка verbose name"""
        post = ModelTest.post
        verbose_author = post._meta.get_field('author').verbose_name
        verbose_group = post._meta.get_field('group').verbose_name
        verbose_list = {
            verbose_author: 'Автор',
            verbose_group: 'Группа',
        }
        for verbose, value in verbose_list.items():
            with self.subTest(value=verbose):
                self.assertEqual(verbose, value)

    def test_models_have_correct_help_text(self):
        """Проверка help_text"""
        post = ModelTest.post
        help_text_text = post._meta.get_field('text').help_text
        help_text_group = post._meta.get_field('group').help_text
        help_text_list = {
            help_text_text: 'Введите текст поста',
            help_text_group: 'Выберите группу',
        }
        for help_text, value in help_text_list.items():
            with self.subTest(value=help_text):
                self.assertEqual(help_text, value)
