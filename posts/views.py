from django.shortcuts import render, get_object_or_404
from .models import Post, Group

def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    return render(request, "index.html", {"posts": latest})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)  
    # функция get_object_or_404 получает по заданным критериям объект из БД
    # или возвращает сообщение об ошибке, если объект не найден
    
    posts = group.posts.order_by("-pub_date")[:12]
    context = {"group": group, "posts": posts}
    return render(request, "group.html", context)