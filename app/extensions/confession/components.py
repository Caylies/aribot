from __future__ import annotations

from contextlib import suppress

import discord
from discord.ui import (
    ActionRow,
    Button,
    Container,
    MediaGallery,
    Modal,
    Label,
    TextInput,
    FileUpload,
    LayoutView,
    TextDisplay
)

from models.models.models import Confession

from .channel import fetch_channel
from .likes import toggle_like
from .utils import random_color


async def sync_confession_message(channel, confession: Confession):
    if not confession.message_id:
        return

    with suppress(discord.NotFound, discord.Forbidden, discord.HTTPException):
        message = await channel.fetch_message(confession.message_id)
        await message.edit(view=await ConfessionView.from_confession(confession))


async def clear_previous_button(channel, before_pk: int):
    previous = await Confession.objects.filter(pk__lt=before_pk).order_by("-pk").afirst()

    if previous is None or not previous.message_id:
        return

    await sync_confession_message(channel, previous)


class ConfessionModal(Modal):
    def __init__(self, reply_confession: Confession | None = None):
        super().__init__(title="Submit Confession")

        self.reply_confession = reply_confession

        self.add_item(TextDisplay(
            "Confessions stay anonymous unless reported three times, "
            "then a moderator reviews the content before seeing who submitted it."
        ))

        self.content = Label(text="Content", component=TextInput(style=discord.TextStyle.paragraph, max_length=1500))
        self.attachment = Label(text="Attachment", component=FileUpload(required=False))
        self.spoiler = Label(
            text="Disclaimer Text",
            description="If text is present, the confession will be marked as a spoiler.",
            component=TextInput(required=False, style=discord.TextStyle.long, max_length=1500)
        )

        self.add_item(self.content)
        self.add_item(self.attachment)
        self.add_item(self.spoiler)

    async def on_submit(self, interaction: discord.Interaction):
        assert interaction.guild

        channel = await fetch_channel(interaction.client)

        if not channel:
            await interaction.response.send_message("Failed to find confession channel.", ephemeral=True)
            return

        if isinstance(channel, (discord.ForumChannel, discord.CategoryChannel, discord.abc.PrivateChannel)):
            await interaction.response.send_message(
                "Confessions cannot be submitted in this channel type.", ephemeral=True
            )
            return

        uploads = self.attachment.component.values
        attachment_url = uploads[0].url if uploads else None

        spoiler_value = self.spoiler.component.value

        confession = await Confession.objects.acreate(
            user_id=interaction.user.id,
            content=self.content.component.value,
            attachment=attachment_url,
            spoiler_text=spoiler_value or None,
        )

        await clear_previous_button(channel, confession.pk)

        await interaction.response.send_message("Your confession has been submitted!", ephemeral=True)

        response_method = channel.send

        if self.reply_confession:
            assert self.reply_confession.message_id

            try:
                reply_message = await channel.fetch_message(self.reply_confession.message_id)
            except Exception:
                pass
            else:
                response_method = reply_message.reply

        message = await response_method(
            view=await ConfessionView.from_confession(confession), allowed_mentions=discord.AllowedMentions.none()
        )
        confession.message_id = message.id

        await confession.asave(update_fields=("message_id",))


class ConfessionView(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

    @classmethod
    async def from_confession(cls, confession: Confession, report_display: bool = False):
        instance = cls()

        is_most_recent = not await Confession.objects.filter(pk__gt=confession.pk).aexists()

        if report_display:
            instance.add_item(TextDisplay(f"Confession (#{confession.pk}) has been reported {confession.reports:,} times."))

        if confession.spoiler_text:
            instance.add_item(TextDisplay(confession.spoiler_text))

        container = Container(
            TextDisplay(f"### Anonymous Confession (#{confession.pk})\n\n\"{confession.content}\""),
            accent_color=random_color(confession.pk),
            spoiler=confession.spoiler_text is not None
        )

        if confession.attachment:
            container.add_item(MediaGallery(discord.MediaGalleryItem(media=confession.attachment)))

        stats: list[tuple[int, str]] = [
            (confession.likes, "💗  {stat}"),
            (confession.reports, "⚠️  {stat}"),
        ]

        final_stats = [stat for stat in stats if stat[0] > 0]

        if final_stats:
            content = "-# "

            for stat in final_stats:
                content += stat[1].format(stat=stat[0]) + "  "

            container.add_item(TextDisplay(content))

        instance.add_item(container)

        if not report_display and is_most_recent:
            instance.add_item(ActionRow(SubmitButton(), LikeButton()))

        return instance


class SubmitButton(Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.primary, label="Submit a confession!", custom_id="confession_submit_button"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ConfessionModal())


class LikeButton(Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.primary, emoji="💗", custom_id="confession_like_button"
        )

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message

        if not message:
            return

        message_id = message.id

        await interaction.response.defer(thinking=True, ephemeral=True)

        liked = await toggle_like(interaction.user.id, await Confession.objects.aget(message_id=message_id))
        confession = await Confession.objects.aget(message_id=message_id)

        await message.edit(view=await ConfessionView.from_confession(confession))

        await interaction.followup.send(f"Like {'added' if liked else 'removed'}.")
