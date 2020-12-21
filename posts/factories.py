import factory, factory.django
from django.contrib.auth.models import User

from posts.models import Group


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'ivan-{n}')
    first_name = factory.Sequence(lambda n: f'ivan-{n}')
    email = factory.Sequence(lambda n: f'ivan-{n}@yandex.ru')


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    title = 'Test title'
    slug = factory.Sequence(lambda x: f'group_{x}')
    description = 'empty'
