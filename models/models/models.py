from django.db import models


class Confession(models.Model):
    user_id = models.BigIntegerField()
    content = models.TextField(max_length=1500)
    attachment = models.URLField(null=True, max_length=2048)
    spoiler_text = models.TextField(max_length=1500, blank=True, null=True)
    reports = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    message_id = models.BigIntegerField(unique=True, null=True)
    # question = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "confession"


class Like(models.Model):
    user_id = models.BigIntegerField()
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "like"
        constraints = [models.UniqueConstraint(fields=("user_id", "confession"), name="unique_like")]
        indexes = [models.Index(fields=("confession",))]


class BotAdmin(models.Model):
    user_id = models.BigIntegerField(unique=True)

    class Meta:
        managed = True
        db_table = "botadmin"
