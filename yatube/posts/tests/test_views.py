from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group
from ..views import COUNT_POST

User = get_user_model()


class ViewPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestAuthorPost")
        cls.user_second = User.objects.create_user(
            username="TestSecondAuthorPost")

        # Первая группа
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание группы",
        )
        # Вторая группа
        cls.group_second = Group.objects.create(
            title="Тестовая группа 2",
            slug="test-slugsecond",
            description="Тестовое описание второй группы",
        )

        # Добавляем посты к user = TestAuthorPost
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая запись 1",
            group=cls.group,
        )
        # Один пост к user_second = TestSecondAuthorPost во вторую групуу
        cls.post_second = Post.objects.create(
            author=cls.user_second,
            text="Тестовая запись 13",
            group=cls.group_second,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_client_user_second = Client()
        self.authorized_client_user_second.force_login(
            self.user_second)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка namespace:name"""
        template = {
            "posts:index": ['posts/index.html', ''],
            "posts:group_list": ["posts/group_list.html", [self.group.slug]],
            "posts:profile": ["posts/profile.html", [self.user.username]],
            "posts:post_detail": ["posts/post_detail.html", [self.post.id]],
            "posts:post_create": ["posts/create_post.html", ""],
            "posts:post_edit": ["posts/create_post.html", [self.post.id]]
        }

        for name, template in template.items():
            template_name, args = template
            with self.subTest(name=name):
                reverse_name = reverse(name, args=args)
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template_name)

    def test_posts_index_page_show_correct_context(self):
        """Шаблон posts/index сформирован с правильным контекстом.
        Ожидаем контекст: список постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        expected_context = {
            'page_obj': None,
        }
        # Проверяем, что типы полей в словаре context соответствуют ожиданиям
        # Method assertIn(a, b), Checks that a in b
        for key, value in expected_context.items():
            self.assertIn(
                key,
                response.context,
                'На Главной странице Index неверный context')
            if not value:
                continue
            self.assertEqual(
                value,
                response.context[key],
                'На Главной странице Index  некорректные значения контекста.')

    def test_posts_group_page_show_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом.
        Ожидаем контекст: список постов отфильтрованных по группе."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug]))
        expected_context = {
            'group': self.group,
            'page_obj': None,
        }
        # Проверяем, что типы полей в словаре context соответствуют ожиданиям
        # Method assertIn(a, b), Checks that a in b
        for key, value in expected_context.items():
            self.assertIn(
                key,
                response.context,
                'На странице список постов group_list неверный context')
            if not value:
                continue
            self.assertEqual(
                value,
                response.context[key],
                'На странице списка постов некорректные значения контекста.')

    def test_posts_profile_page_show_correct_context(self):
        """Шаблон posts/profile сформирован с правильным контекстом.
        Ожидаем контекст: список постов отфильтрованных по пользователю."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.user.username]))
        expected_context = {
            'username': self.user,
            'post_count':
                Post.objects.filter(author=self.user).count(),
            'page_obj': None
        }

        for key, value in expected_context.items():
            self.assertIn(
                key,
                response.context,
                'На странице профиля Profile неверный context')
            if not value:
                continue
            self.assertEqual(
                value,
                response.context[key],
                'На странице профиля Profile некорректные значения контекста.')

    def test_posts_detail_pages_show_correct_context(self):
        """Шаблон posts/post_detail сформирован с правильным контекстом.
        Ожидаем контекст: один пост, отфильтрованный по id поста."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id]))
        expected_context = {
            'post': self.post,
            'post_number':
                Post.objects.filter(author=self.user).count()
        }

        for key, value in expected_context.items():
            self.assertIn(
                key,
                response.context,
                'На странице детали поста post_detail неверный context')
            if not value:
                continue
            self.assertEqual(
                value,
                response.context[key],
                'На странице post_detail некорректные значения контекста.')

    def test_post_edit_show_correct_context(self):
        """Шаблон posts/post_edit сформирован с правильным контекстом.
        Форма редактирования поста, отфильтрованного по id."""
        response = (self.authorized_client.get(
            reverse('posts:post_edit', args=[self.post.id]))
        )
        expected_context = {
            'title': 'Редактирование поста',
        }

        for key, value in expected_context.items():
            self.assertIn(
                key,
                response.context,
                'На странице редактирования поста неверный context')
            if not value:
                continue
            self.assertEqual(
                value,
                response.context[key],
                'На странице редактирования поста некорректные'
                'значения контекста.')

    def test_posts_create_post_correct_context(self):
        """Шаблон posts/post_create сформирован с правильным контекстом.
        Форма создания нового поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        expected_context = {
            'title': 'Создание нового поста',
        }

        for key, value in expected_context.items():
            self.assertIn(
                key,
                response.context,
                'На странице создание поста post_create неверный context')
            if not value:
                continue
            self.assertEqual(
                value,
                response.context[key],
                'На странице post_create некорректные значения контекста.')

    def test_posts_group_page_not_include_incorect_post(self):
        """Шаблон posts/group_list не содержит лишний пост. Проверьте,
        что этот пост не попал в группу, для которой не был предназначен."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slugsecond"})
        )
        for second_group_post in response.context["page_obj"]:
            self.assertNotEqual(second_group_post.pk, self.post.pk)

    def test_new_post_show_on_index_group_list_profile(self):
        """Проверка, если при создании поста указать группу,то пост появляется:
        на главной странице сайта;на странице выбранной группы."""
        form_data_in_post = {
            'text': 'Новый тестовый пост',
            'group': self.group_second.id,
        }

        assert_methods_and_namespase = {
            None: [self.assertEqual, 'posts:index'],
            self.group_second.slug: (self.assertEqual, 'posts:group_list'),
            self.user.username: (self.assertEqual, 'posts:profile'),
            self.group.slug: (self.assertNotEqual, 'posts:group_list'),
            self.user_second.username: (self.assertNotEqual, 'posts:profile')
        }

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_in_post
        )
        last_post = Post.objects.latest('id')

        for args, value in assert_methods_and_namespase.items():
            assert_method, name = value
            with self.subTest(name=name):
                if not args:
                    continue
                reverse_name = reverse(name, args=[args])
                response = self.authorized_client.get(
                    reverse_name,
                    follow=True
                )
                last_post_page = response.context.get('page_obj')[0]
                assert_method(last_post_page, last_post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем автора и группу для теста Paginatora."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='author_paginator',)
        cls.group = Group.objects.create(
            title=('Группа для Паджинатора'),
            slug='paginator-slug',
            description='Тестовое описание для Паджинатора'
        )

    def setUp(self):
        """Создаем клиента и 14 постов для теста(10+4)."""
        self.client = Client()
        self.count_of_posts_to_create = 14
        for post in range(self.count_of_posts_to_create):
            Post.objects.create(
                author=self.author,
                text=f'test_text_{post}',
                group=self.group)

    def test_page_index_paginator(self):
        """Проверяем пагинацию страницы for index."""
        self._check_pagination_correct(
            reverse('posts:index'),
            COUNT_POST
        )
        self._check_pagination_correct(
            reverse('posts:index') + '?page=2',
            self.count_of_posts_to_create % COUNT_POST
        )

    def test_page_group_list_paginator(self):
        """Проверяем пагинацию страницы for group_list."""
        self._check_pagination_correct(
            reverse('posts:group_list', args=[self.group.slug]),
            COUNT_POST
        )
        self._check_pagination_correct(
            reverse('posts:group_list', args=[self.group.slug]) + '?page=2',
            self.count_of_posts_to_create % COUNT_POST
        )

    def test_page_posts_profile_paginator(self):
        """Проверяем пагинацию страницы for profile."""
        self._check_pagination_correct(
            reverse('posts:profile', args=[self.author.username]),
            COUNT_POST
        )
        self._check_pagination_correct(
            reverse('posts:profile', args=[self.author.username]) + '?page=2',
            self.count_of_posts_to_create % COUNT_POST
        )

    def _check_pagination_correct(self, page: str, expected: int):
        """Сравниваем кол-во постов на странице с ожидаемым результатом."""
        response = self.client.get(page)
        count_posts_on_page = len(response.context['page_obj'])
        self.assertEqual(count_posts_on_page, expected)
