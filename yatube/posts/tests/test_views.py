from django.contrib.auth import get_user_model
from django import forms
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
        object = response.context['page_obj'][1]
        context_objects = {
            object.author.username: self.post.author.username,
            object.text: self.post.text,
            object.group.title: self.post.group.title,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)
        # object = response.context["page_obj"][0]
        # post_text = object.text
        # post_group = object.group
        # post_author = object.author
        # self.assertEqual(post_text, "Тестовая запись 13")
        # self.assertEqual(post_group, self.group_second)
        # self.assertEqual(post_author, self.user_second)

    '''
    def test_posts_index_page_first_show_ten_items(self):
        """Шаблон posts/index первая страница содержит 10 постов.
        Ожидаем контекст: список постов. Пагинатор"""
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), COUNT_POST)

    def test_posts_index_page_second_show_three_items(self):
        """Шаблон posts/index вторая страница содержит 3 поста.
        Ожидаем контекст: список постов. Пагинатор"""
        response = self.authorized_client.get(
            reverse("posts:index") + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 3)
    '''

    def test_posts_group_page_show_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом.
        Ожидаем контекст: список постов отфильтрованных по группе."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={"slug": self.post.group.slug}))
        object = response.context['page_obj'][0]
        self.assertEqual(self.post.group.title, object.group.title)
        self.assertEqual(self.post.group.slug, object.group.slug)
        # response = self.guest_client.get(
        #    reverse("posts:group_list", kwargs={"slug": "test-slug"}))
        # object = response.context["page_obj"][0]
        # post_text = object.text
        # post_group = object.group
        # post_author = object.author
        # self.assertEqual(post_text, "Тестовая запись 1")
        # self.assertEqual(post_group, self.group)
        # self.assertEqual(post_author, self.user)

    '''
    def test_posts_group_page_first_show_ten_items(self):
        """Шаблон posts/group_list первая страница содержит 10 записей.
        Пагинатор."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
        )
        self.assertEqual(len(response.context["page_obj"]), COUNT_POST)

    def test_posts_group_page_second_show_two_items(self):
        """Шаблон posts/group_list вторая страница содержит 2 записи.
        Пагинатор."""

        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 2)
    '''

    def test_posts_profile_page_show_correct_context(self):
        """Шаблон posts/profile сформирован с правильным контекстом.
        Ожидаем контекст: список постов отфильтрованных по пользователю."""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthorPost"}))
        object = response.context["page_obj"][0]
        post_text = object.text
        post_group = object.group
        post_author = object.author
        self.assertEqual(post_text, "Тестовая запись 1")
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_author, self.user)

    '''
    def test_posts_user_page_first_show_ten_items(self):
        """Шаблон posts/profile первая страница содержит 10 записей.
        Пагинатор."""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthorPost"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_posts_user_page_first_show_ten_items(self):
        """Шаблон posts/profile первая страница содержит 2 записи.
        Пагинатор"""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthorPost"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 2)
    '''

    def test_posts_detail_pages_show_correct_context(self):
        """Шаблон posts/post_detail сформирован с правильным контекстом.
        Ожидаем контекст: один пост, отфильтрованный по id поста."""
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk})
        )
        self.assertEqual(response.context.get('post').text,
                         "Тестовая запись 1")
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(response.context.get('post').author, self.user)

    def test_post_edit_show_correct_context(self):
        """Шаблон posts/post_edit сформирован с правильным контекстом.
        Форма редактирования поста, отфильтрованного по id."""
        response = (self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_create_post_correct_context(self):
        """Шаблон posts/post_create сформирован с правильным контекстом.
        Форма создания нового поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields[value]
                self.assertIsInstance(form_field, expected)

    '''def test_post_right_group_exists(self):
        """Проверка Создания Поста, если при создании поста выбрать группу"""
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        object = self.group.posts.filter(
            group=response.context.get("post").group
        )
        self.assertTrue(object.exists())
        response = self.authorized_client.get(reverse(
            "posts:group_list", kwargs={"slug": self.group.slug})
        )
        object = self.group.posts.filter(
            group=response.context.get("post").group
        )
        self.assertTrue(object.exists())'''

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
            reverse('posts:group_list', self.group.slug),
            COUNT_POST
        )
        self._check_pagination_correct(
            reverse('posts:group_list', self.group.slug) + '?page=2',
            self.count_of_posts_to_create % COUNT_POST
        )

    def test_page_group_list_paginator(self):
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
