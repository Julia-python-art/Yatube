from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from .models import Post, Group, Follow
from django.urls import reverse

from .factories import GroupFactory


class TestPage(TestCase):
    def test_page_404(self):
        client = Client()
        response = self.client.get("group/nothing/")
        self.assertEqual(response.status_code, 404)



class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
                    username="sarah", 
                    email="connor@skynet.com", 
                    password="12345")
        
        self.client.login(username="sarah", password="12345")

        self.text = "It's driving me crazy!"
        self.edit = "Deleted"
        self.title = "Test group"
        self.slug = "test_group"
        self.description = "test test test"
        self.group = Group.objects.create(
                                    title=self.title,
                                    slug=self.slug,
                                    description=self.description)
       

    
    def test_profile(self):

        response = self.client.get(reverse("profile", 
                            kwargs={"username": self.user.username}))
        
        self.assertEqual(response.status_code, 200)


    def test_auth_user_create_post(self):

        response = self.client.get(reverse("new_post"))
        self.client.post(response, {"text": self.text, 
                                    "group": self.group.id}, 
                                    follow=True)
        self.assertEqual(response.status_code, 200)


    def test_anonim_create_post(self):

        self.client.logout()
        response = self.client.get(reverse("new_post"), follow=True)
        self.client.post(response, {"text": self.text,
                                    "group": self.group.id}, 
                                    follow=True)
        self.assertRedirects(response, "/auth/login/?next=/new/new/")


    def get_urls(self, post):
        urls = [
                reverse("index"),
                reverse("profile", kwargs={"username": post.author}),
                reverse("post", kwargs={"username": post.author, 
                                       "post_id": post.id}),
                reverse("group", kwargs={"slug": self.slug})                       
                ]

        return urls


    def check(self, url, user, group, text, new_text):

        self.client.get(url)
        self.assertEqual(user, self.user)
        self.assertEqual(text, self.text)
        self.assertEqual(new_text, self.edit)
        self.assertEqual(group, self.group)


    def test_new_post_location(self):

        post = Post.objects.create(
                            text=self.text,
                            author=self.user,
                            group=self.group)

        self.client.post(
                    reverse("new_post"),
                    data={"text": self.text,
                        "group": self.group.id},
                    follow=True)

        for url in (self.get_urls(post=post)):
            self.check(url, self.user, self.group, self.text, self.edit)



    def test_edit_post(self):

        post = Post.objects.create(
                        text=self.text,
                        author=self.user,
                        group=self.group)

        self.client.post(
                    reverse("post_edit",
                    kwargs={"username": post.author,
                            "post_id": post.id}),
                    data={"text": self.edit,
                        "group": self.group.id},
                    follow=True)

        for url in (self.get_urls(post=post)):
            self.check(url, self.user, self.group, self.text, self.edit)




class TestIndexPage(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_index_available(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class TestGroups(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def tearDown(self) -> None:
        Group.objects.filter(slug="first_group").delete()

    def test_page_not_found(self):
        response = self.client.get("group/not_exist/")
        self.assertEqual(response.status_code, 404)

    def test_exists_group(self):
        group = Group.objects.create(
            title="test",
            slug="first_group",
            description="empty")    
        response = self.client.get(reverse("group",
                                kwargs={"slug": group.slug}))
        self.assertEqual(response.status_code, 200)


class TestPosts(TestCase):
    def setUp(self) -> None:
        self.auth_client = Client()
        user = User.objects.create(username="test_user", email="q@q.com")
        user.set_password("123")
        user.save()
        self.auth_client.login(username="test_user", password="123")

    def tearDown(self) -> None:
        Group.objects.filter(
            title="test",
            slug="first_group",
            description="empty"
        ).delete()

        User.objects.filter(username="test_user").delete()

    def test_valid_form(self):
        group = Group.objects.create(
            title="test",
            slug="first_group",
            description="empty"
        )
        group_id = f'{group.id}'
        self.auth_client.post(
            "/new/",
            data={
                "text": "test text",
                "group": group_id
            }
        )

        self.assertTrue(
            Post.objects.filter(text="test text", group=group_id).exists()
        )

    def test_form_not_valid(self):
        response = self.auth_client.post(
            "/new/",
            data={
                "group": "100500"
            }
        )

        self.assertFormError(
            response,
            form="form",
            field="text",
            errors=["Обязательное поле."]
        )


class TestImage(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
                    username="sarah", 
                    email="connor@skynet.com", 
                    password="12345")
        
        self.client.login(username="sarah", password="12345")


        self.text = "It's driving me crazy!"
        self.title = "Test group"
        self.slug = "test_group"
        self.description = "test test test"
        self.group = Group.objects.create(
                                    title=self.title,
                                    slug=self.slug,
                                    description=self.description)


        self.post = Post.objects.create(
                    text=self.text,
                    author=self.user,
                    group=self.group)                            


    def test_image_available(self):
        with open("media/1.jpg","rb") as img:
            self.client.post(
                        reverse("post_edit",
                        kwargs={"username": self.user.username,
                                "post_id": self.post.id}),
                        data={"text": self.text, 
                            "group": self.group.id,
                            "image": img}, follow=True)

        pages = [
            "/",
            reverse("profile", kwargs={"username": self.user.username}),
            reverse("group", kwargs={"slug": self.group.slug})
        ]

        for page in pages:
            response = self.client.get(page)
            self.assertContains(response, "img")


    def test_not_image(self):
        with open("media/2.txt","rb") as img:
            self.client.post(
                        reverse("post_edit",
                        kwargs={"username": self.user.username,
                                "post_id": self.post.id}),
                        data={"text": self.text, 
                            "group": self.group.id,
                            "image": img}, follow=True)

        pages = [
            "/",
            reverse("profile", kwargs={"username": self.user.username}),
            reverse("group", kwargs={"slug": self.group.slug})
        ]
        
        for page in pages:
            response = self.client.get(page)
            self.assertNotContains(response, "img")



class TestCache(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
                    username="sarah", 
                    email="connor@skynet.com", 
                    password="12345")
        
        self.client.login(username="sarah", password="12345")

        self.post = Post.objects.create(
                    text="test cache",
                    author=self.user)

    def test_cache_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test cache")
        self.post = Post.objects.create(
                    text="test cache1",
                    author=self.user)
        response = self.client.get("/")           
        self.assertNotContains(response, "test cache1")


class TestFollowComment(TestCase):
    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        
        self.user1 = User.objects.create_user(
                    username="tom", 
                    email="tom@.com", 
                    password="000000")

        self.user2 = User.objects.create_user(
                    username="jerry", 
                    email="jerry@.com", 
                    password="111111")              
        
        self.client1.login(username="tom", password="000000")
  
        
    def test_can_follow(self):      
        self.client1.get(reverse("profile_follow", args=["jerry"]), follow=True)
        follow = Follow.objects.all().count() 
        self.assertEqual(follow, 1)


    def test_can_unfollow(self):
        self.client1.get(reverse("profile_unfollow", args=["jerry"]), follow=True)
        follow = Follow.objects.all().count()
        self.assertEqual(follow, 0)


    def test_auth_comment(self):
        post = Post.objects.create(
                    text="Tom and Jerry",
                    author=self.user1)

        response = self.client1.post(
                    reverse("add_comment",
                     kwargs={"username": "tom", "post_id": post.id}),
                     {"text": "Tom Tom"},
                    follow=True)
        self.assertEqual(response.status_code, 200)


    def test_not_auth_comment(self):
        post = Post.objects.create(
                    text="Tom and Jerry",
                    author=self.user1)
        
        response = self.client2.post(
                    reverse("add_comment",
                     kwargs={"username": "tom", "post_id": post.id}),
                     {"text": "Tom Tom"},
                    follow=True)
        self.assertRedirects(response, f"/auth/login/?next=/new/{self.user1.username}/{post.id}/comment") 



    def test_follow_index(self):       
        self.client2.login(username="jerry", password="111111")
        post_jerry = Post.objects.create(
                    text="jerry",
                    author=self.user2)
        
        self.client1.get(reverse("profile_follow",
                            args=["jerry"]), follow=True)                
                         
        response_tom = self.client1.get("/follow/")
        self.assertContains(response_tom, post_jerry.text)


        post_tom = Post.objects.create(
                    text="tom",
                    author=self.user1)

        response_jerry = self.client2.get("/follow/")
        self.assertNotContains(response_jerry, post_tom.text)                               