from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse

from .forms import PostForm, CommentForm
from .models import Group, Post, User


COUNT_POST = 10


def index(request):
    """Главная страница."""
    posts = Post.objects.select_related('author', 'group')
    paginator = Paginator(posts, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница списка групп постов."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Cписок постов пользователя, информация о пользователе."""
    username = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=username)
    post_count = user_posts.count()
    paginator = Paginator(user_posts, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'username': username,
        'page_obj': page_obj,
        'post_count': post_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница поста пользоввателя и общее количество постов."""
    post = get_object_or_404(Post, id=post_id)
    post_number = Post.objects.filter(author=post.author).count()
    post_comment = post.text
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'post_number': post_number,
        'post_comment': post_comment,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Добавление нового поста."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
    title = 'Создание нового поста'
    context = {
        'title': title,
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Cтраница редактирования постов"""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    title = 'Редактирование поста'
    context = {
        'post': post,
        'form': form,
        'title': title,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    # Получите пост и сохраните его в переменную post.
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(reverse('posts:post_detail',
                        kwargs={'post_id': post_id}))
    return render(request, 'posts/post_detail.html',
                  {'form': form, 'post': post})
