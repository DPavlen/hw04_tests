from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import POST_TEXT
from ..models import Group, Post

User = get_user_model()
# POST_TEXT = 15


class PostModelTest(TestCase):
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
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.group = PostModelTest.group
        self.assertEqual(str(self.group), self.group.title)

        self.post = PostModelTest.post
        self.assertEqual(str(self.post), self.post.text[:POST_TEXT])