from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название сообщества")
    
    slug = models.SlugField(unique=True, verbose_name="Адрес")
    
    description = models.TextField(verbose_name="Краткое описание")

    def __str__(self):
      return self.title



class Post(models.Model):
    text = models.TextField(verbose_name="Текст поста", 
                            help_text="Удиви мир своими идеями!")
    
    pub_date = models.DateTimeField(verbose_name="Дата публикации", 
                                    auto_now_add=True)
    
    author = models.ForeignKey(User, 
                              on_delete=models.CASCADE,
                              related_name="posts", 
                              verbose_name="Автор")
    
    group = models.ForeignKey(Group, 
                              on_delete=models.CASCADE,
                              related_name="posts", 
                              blank=True, 
                              null=True,
                              verbose_name="Сообщество",
                              help_text="Выберите сообщество из списка "
                                        "или оставьте это поле пустым")
    
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    def __str__(self):
      return self.text



class Comment(models.Model):
  post = models.ForeignKey(Post,
                      on_delete=models.CASCADE,
                      related_name="comments",
                      blank=True,
                      null=True,
                      verbose_name="Комментарий",
                      help_text="Вы можете оставить свой комментарий")

  author = models.ForeignKey(User,
                    on_delete=models.CASCADE,
                    related_name="comments",
                    verbose_name="Автор")

  text = models.TextField(verbose_name="Текст комментария", 
                          help_text="Оставьте свой комментарий")

  created = models.DateTimeField(auto_now_add=True,
                                verbose_name="Дата публикации")

  def __str__(self):
    return self.text



class Follow(models.Model):
  user = models.ForeignKey(User,
                on_delete=models.CASCADE,
                related_name="follower", 
                verbose_name="Подписчик")
  author = models.ForeignKey(User,
                on_delete=models.CASCADE,
                related_name="following",
                verbose_name="Автор")              
