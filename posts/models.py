from django.conf import settings
from django.db import models

class Post(models.Model):
    """
    Represents a single post on the bulletin board.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        help_text="The user who created the post."
    )
    content = models.TextField(
        help_text="The content of the post."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="The date and time the post was created."
    )
    likes_count = models.PositiveIntegerField(
        default=0,
        help_text="Cached count of likes for performance."
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class PostLike(models.Model):
    """
    Represents a 'like' on a Post by a User.
    This model ensures that a user can only like a post once.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_likes"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This constraint ensures that a user can only like a specific post once.
        # This was a point of discussion and is implemented here to ensure data integrity.
        unique_together = ("user", "post")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes {self.post}"
