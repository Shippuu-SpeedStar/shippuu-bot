import discord


async def join_vc(interaction: discord.Interaction):
    # コマンド実行者がVCに参加しているか確認
    if interaction.user.voice is None:
        await interaction.response.send_message(
            "❌ 先にボイスチャンネルへ参加してください。",
            ephemeral=True
        )
        return

    voice_channel = interaction.user.voice.channel

    # BotがすでにVCに接続している場合
    if interaction.guild.voice_client is not None:
        voice_client = interaction.guild.voice_client

        # 同じVCにいる場合
        if voice_client.channel == voice_channel:
            await interaction.response.send_message(
                f"🔊 すでに **{voice_channel.name}** に参加しています。",
                ephemeral=True
            )
            return

        # 別のVCにいる場合は移動
        await voice_client.move_to(voice_channel)

        await interaction.response.send_message(
            f"🔊 **{voice_channel.name}** に移動しました。"
        )
        return

    # VCへ接続
    await voice_channel.connect()

    await interaction.response.send_message(
        f"🔊 **{voice_channel.name}** に参加しました。"
    )


async def leave_vc(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    # BotがVCに参加していない場合
    if voice_client is None:
        await interaction.response.send_message(
            "❌ 現在ボイスチャンネルに参加していません。",
            ephemeral=True
        )
        return

    channel_name = voice_client.channel.name

    await voice_client.disconnect()

    await interaction.response.send_message(
        f"👋 **{channel_name}** から退出しました。"
    )
