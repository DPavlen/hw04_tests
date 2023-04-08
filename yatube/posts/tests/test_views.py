from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group
from django import forms
# from django.shortcuts import get_object_or_404

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
            title="Тестовая группа",
            slug="test-slugsecond",
            description="Тестовое описание второй группы",
        )

        # Добавляем посты к user = TestAuthorPost
        cls.post = []
        for i in range(12):
            cls.post.append(
                Post.objects.create(
                    author=cls.user,
                    text=f"Тестовая запись {i}",
                    group=cls.group,
                )
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
        page_number_template = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:group_list", kwargs={"slug": "test-slug"}
                    ): "posts/group_list.html",
            reverse("posts:profile", kwargs={"username": "TestAuthorPost"}
                    ): "posts/profile.html",
            reverse("posts:post_detail", kwargs={"post_id": self.post[0].pk}
                    ): "posts/post_detail.html",
            reverse("posts:post_edit", kwargs={"post_id": self.post[0].pk}
                    ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }

        # Проверяем, что при обращении к index вызывается HTML-шаблон
        for reverse_name, template in page_number_template.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_index_page_show_correct_context(self):
        """Шаблон posts/index сформирован с правильным контекстом.
        Ожидаем контекст: список постов."""
        response = self.guest_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, "Тестовая запись 13")
        self.assertEqual(post_group_0, self.group_second)
        self.assertEqual(post_author_0, self.user_second)

    def test_posts_index_page_first_show_three_items(self):
        """Шаблон posts/index первая страница содержит 10 постов.
        Ожидаем контекст: список постов. Пагинатор"""
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_posts_index_page_second_show_three_items(self):
        """Шаблон posts/index вторая страница содержит 3 поста.
        Ожидаем контекст: список постов. Пагинатор"""
        response = self.authorized_client.get(
            reverse("posts:index") + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_posts_group_page_show_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом.
        Ожидаем контекст: список постов отфильтрованных по группе."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"}))
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, "Тестовая запись 11")
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)

    def test_posts_group_page_first_show_ten_items(self):
        """Шаблон posts/group_list первая страница содержит 10 записей.
        Пагинатор."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_posts_group_page_second_show_two_items(self):
        """Шаблон posts/group_list вторая страница содержит 2 записи.
        Пагинатор."""

        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 2)

    def test_posts_profile_page_show_correct_context(self):
        """Шаблон posts/profile сформирован с правильным контекстом.
        Ожидаем контекст: список постов отфильтрованных по пользователю."""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthorPost"}))
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, "Тестовая запись 11")
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)

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

    def test_posts_detail_pages_show_correct_context(self):
        """Шаблон posts/post_detail сформирован с правильным контекстом.
        Ожидаем контекст: один пост, отфильтрованный по id поста."""
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post[0].pk})
        )
        self.assertEqual(response.context.get('post').text,
                         "Тестовая запись 0")
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(response.context.get('post').author, self.user)

    def test_post_edit_show_correct_context(self):
        """Шаблон posts/post_edit сформирован с правильным контекстом.
        Форма редактирования поста, отфильтрованного по id."""
        response = (self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post[1].pk}))
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
        response = self.authorized_client.get(reverse("1",))
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
        for secong_group_post in response.context["page_obj"]:
            self.assertNotEqual(secong_group_post.pk, self.post[0].pk)
