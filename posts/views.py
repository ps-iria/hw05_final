from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import InvalidPage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, Follow

User = get_user_model()


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = pagination(paginator, page_number)
    return render(
        request,
        "index.html",
        {
            "page": page,
            "paginator": paginator,
        }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = pagination(paginator, page_number)
    return render(
        request,
        "group.html",
        {
            "group": group,
            "page": page,
            "paginator": paginator,
        }
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = pagination(paginator, page_number)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    return render(
        request,
        "profile.html",
        {
            "page": page,
            'paginator': paginator,
            "author": author,
            'following': following,
        }
    )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    form = CommentForm()
    comments = Comment.objects.filter(post=post)[:10]
    return render(
        request,
        "post_detail.html",
        {
            'post': post,
            'author': author,
            'comments': comments,
            'form': form,
        }
    )


def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        return redirect('post_detail', username=username, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id, author=author)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        return render(
            request,
            'post_new.html',
            {
                'form': form,
                'post': post
            }
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('post_detail', username=username, post_id=post_id)


def pagination(paginator, page_number):
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    except InvalidPage:
        page = paginator.page(1)
    return page


@login_required
def create_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(
            request,
            'post_new.html',
            {
                'form': form
            }
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {
            "path": request.path
        },
        status=404
    )


def server_error(request):
    return render(
        request,
        "misc/500.html",
        status=500
    )


@login_required
def add_comment(request, username, post_id):
    post_object = get_object_or_404(Post, id=post_id,
                                    author__username=username)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post_object
            comment.author = request.user
            comment.save()
            return redirect('post_detail', username=username, post_id=post_id)
        return render(
            request,
            'comments.html',
            {
                'form': form,
                'post': post_object
            }
        )
    form = CommentForm()
    return render(
        request,
        'comments.html',
        {
            'form': form,
            'post': post_object
        }
    )


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = pagination(paginator, page_number)
    return render(
        request,
        "follow.html",
        {
            "page": page,
            "paginator": paginator,
        }
    )


@login_required
def profile_follow(request, username):
    follow_object = Follow.objects.filter(author__username=username,
                                          user=request.user).exists()
    if request.user.username == username:
        return redirect('profile', username=username)
    if not follow_object:
        follower = get_object_or_404(User, username=username)
        follow = Follow.objects.create(user=request.user, author=follower)
        follow.save()
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    follow_object = get_object_or_404(Follow, author__username=username,
                                      user=request.user)
    follow_object.delete()
    return redirect('profile', username=username)


@login_required
def comment_edit(request, username, post_id, comment_id):
    author = get_object_or_404(User, username=request.user)
    if request.user != author:
        return redirect('post_detail', username=username, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id, author=author)
    comment = get_object_or_404(Comment, pk=comment_id, post=post,
                                author=author)
    comments = Comment.objects.filter(post=post)[:10]
    form = CommentForm(request.POST or None,
                       instance=comment)
    if not form.is_valid():
        return render(
            request,
            'post_detail.html',
            {
                'post': post,
                'author': author,
                'comments': comments,
                'form': form,
                'comment': comment
            }
        )
    comment = form.save(commit=False)
    comment.save()
    return redirect('post_detail', username=username, post_id=post_id)


@login_required
def comment_delete(request, username, post_id, comment_id):
    author = get_object_or_404(User, username=request.user)
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post,
                                author=author)
    comment.delete()
    return redirect('post_detail', username=username, post_id=post_id)
