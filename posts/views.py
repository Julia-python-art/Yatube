from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm

from django.contrib.auth.models import User



def page_not_found(request, exception):
    """ Страница не найдена, ошибка 404 """
    return render(request, 
                "misc/404.html",
                {"path": request.path},
                status=404)



def server_error(request):
    """ Страница не найдена, ошибка 500 """
    return render(request,"misc/500.html", status=500)             



@cache_page(20)
def index(request):
    """ Главная страница сайта """
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)

    # переменная в URL с номером запрошенной страницы
    page_number = request.GET.get("page")
    # получить записи с нужным смещением
    page = paginator.get_page(page_number)

    return render(request, "index.html", 
            {"page": page, 
            "paginator": paginator})


def group_posts(request, slug):
    """ Отображение групп """
    group = get_object_or_404(Group, slug=slug)  
    # функция get_object_or_404 получает по заданным критериям объект из БД
    # или возвращает сообщение об ошибке, если объект не найден
    
    group_list = group.posts.order_by("-pub_date").all()
    paginator = Paginator(group_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {"page": page, 
              "paginator": paginator,
              "group": group}

    return render(request, "group.html", context)


@login_required
def new_post(request):
    """ Добавить новую запись, если пользователь авторизован """
    if request.method == "POST":
        form = PostForm(request.POST or None, 
                    files=request.FILES or None)
        
        if form.is_valid():
            post = form.save(commit=False)
            #  вернет объект, который еще не сохранен в БД.
            post.author = request.user
            post.save()
            return redirect("/")
        return render(request, "new_post.html", {"form": form})
    form = PostForm()
    return render(request, "new_post.html", {"form": form})



class PostView(CreateView):
    form_class = PostForm
    success_url = "index"
    template_name = "new_post"


def profile(request, username):
    """ Страница со всеми постами пользователя """
    user_name = get_object_or_404(User, username=username)
    user_posts =  user_name.posts.all()
    following = Follow.objects.filter(user=request.user.id, author=user_name.id).all()

    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, 'profile.html',
            {"page": page, 
            "paginator": paginator, 
            "following": following,
            "user_name": user_name,
            "user_posts": user_posts})
 


def post_view(request, username, post_id):
    """ Страница просмотра отдельного поста """
    user_name = get_object_or_404(User, username=username)
    post =  get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    return render(request, 'post.html', 
            {"user_name": user_name, 
            "comments": comments,
            "form" : form,
            "post": post})


@login_required
def post_edit(request, username, post_id):
    """ Редактировать свой пост, если пользователь авторизован """
    profile = get_object_or_404(User, username=username)
    edited_post =  get_object_or_404(Post, 
                                    id=post_id, 
                                    author=profile)
    if request.user != profile:
        return redirect("post", username, post_id)
    
    form = PostForm(request.POST or None, 
                    files=request.FILES or None, 
                    instance=edited_post)
    
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post", username, post_id)
    
    return render(request, "new_post.html",
                {"form": form,
                "edited_post": edited_post,
                "username": username,
                "post_id": post_id})        


@login_required
def add_comment(request, username, post_id):
    """ Добавить комментарий """
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id = post_id)
    comments = post.comments.all()
    
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            form.save()
            return redirect("post", username, post_id)
        
        return render(request, "post.html",
                {"form": form,
                "user": user,
                "post": post,
                "comments": comments})
    
    form = CommentForm()
    return render(request, "post.html",
                {"form": form,
                "user": user,
                "post": post,
                "comments": comments})            


@login_required
def follow_index(request):
    """ Страница со всеми подписками пользователя """
    follow = User.objects.get(id=request.user.id).follower.all().values_list("author")
    post_list = Post.objects.filter(author__in=follow).order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    
    return render(request, "follow.html", 
                {"paginator": paginator, 
                "page": page,
                "post_list": post_list}) 


@login_required
def profile_follow(request, username):
    """ Подписаться на автора """
    user = get_object_or_404(User, username=request.user)
    author = get_object_or_404(User, username=username)
    
    if user == author:
        return redirect("profile", username)
    
    follow = Follow.objects.filter(user=user, author=author)
    if len(follow) > 0:
        return redirect("profile", username)
    
    Follow.objects.create(user=user, author=author)
    
    return redirect("profile", username)        


@login_required
def profile_unfollow(request, username):
    """ Отписаться от автора """
    user = get_object_or_404(User, username=request.user)
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=user, author=author)

    follow.delete()

    return redirect("profile", username)  