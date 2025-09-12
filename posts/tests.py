from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from .models import Post, PostLike

User = get_user_model()

class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="password")

    def test_create_post(self):
        """Test creating a new post."""
        post = Post.objects.create(
            author=self.user,
            content="This is a test post."
        )
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.content, "This is a test post.")
        self.assertEqual(post.likes_count, 0)
        self.assertIsNotNone(post.created_at)

    def test_post_like(self):
        """Test liking a post."""
        post = Post.objects.create(author=self.user, content="Another post")
        like = PostLike.objects.create(user=self.user, post=post)
        self.assertEqual(PostLike.objects.count(), 1)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.post, post)

    def test_unique_like_constraint(self):
        """Test that a user cannot like the same post twice."""
        post = Post.objects.create(author=self.user, content="A post to be liked")
        # First like should be successful
        PostLike.objects.create(user=self.user, post=post)
        self.assertEqual(PostLike.objects.count(), 1)

        # Second like should fail, which proves the constraint
        with self.assertRaises(IntegrityError):
            PostLike.objects.create(user=self.user, post=post)
