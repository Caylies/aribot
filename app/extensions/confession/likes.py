from django.db.models import F

from models.models.models import Confession, Like


async def toggle_like(user_id: int, confession: Confession) -> bool:
    like, created = await Like.objects.aget_or_create(
        user_id=user_id, confession=confession
    )

    amount = 1

    if not created:
        await like.adelete()
        amount = -1

    await Confession.objects.filter(pk=confession.pk).aupdate(likes=F("likes") + amount)
    await confession.arefresh_from_db()
    return created
