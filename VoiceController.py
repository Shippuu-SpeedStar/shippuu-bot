import discord
import asyncio


async def join_vc(interaction: discord.Interaction):
    # 接続処理に時間がかかる可能性があるため、先に応答を保留する
    await interaction.response.defer(ephemeral=True)

    # DMなどGuild外から実行された場合
    if interaction.guild is None:
        await interaction.followup.send(
            "❌ サーバー内で実行してください。",
            ephemeral=True
        )
        return

    # 実行者がVCに参加しているか
    if interaction.user.voice is None:
        await interaction.followup.send(
            "❌ 先にボイスチャンネルへ参加してください。",
            ephemeral=True
        )
        return

    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    # Bot側にVoiceClientが残っている場合
    if voice_client is not None:

        # 実際に接続済みか確認
        if voice_client.is_connected():

            # 同じVC
            if voice_client.channel == voice_channel:
                await interaction.followup.send(
                    f"🔊 すでに **{voice_channel.name}** に参加しています。",
                    ephemeral=True
                )
                return

            # 別VCなら移動
            try:
                await voice_client.move_to(voice_channel)

                await interaction.followup.send(
                    f"🔊 **{voice_channel.name}** に移動しました。",
                    ephemeral=True
                )

            except Exception as e:
                print(f"[Voice] VC移動エラー: {e}")

                await interaction.followup.send(
                    "❌ ボイスチャンネルへの移動に失敗しました。",
                    ephemeral=True
                )

            return

        # VoiceClientは存在するが、実際には切断されている
        try:
            await voice_client.disconnect(force=True)
        except Exception as e:
            print(f"[Voice] 古いVoiceClient削除エラー: {e}")

    # 新しくVCへ接続
    try:
        voice_client = await asyncio.wait_for(
            voice_channel.connect(
                timeout=20.0,
                reconnect=True
            ),
            timeout=25.0
        )

        await interaction.followup.send(
            f"🔊 **{voice_channel.name}** に参加しました。",
            ephemeral=True
        )

    except asyncio.TimeoutError:
        print("[Voice] VC接続タイムアウト")

        # 中途半端にVoiceClientが残っていたら削除
        voice_client = interaction.guild.voice_client

        if voice_client is not None:
            try:
                await voice_client.disconnect(force=True)
            except Exception:
                pass

        await interaction.followup.send(
            "❌ ボイスチャンネルへの接続がタイムアウトしました。",
            ephemeral=True
        )

    except Exception as e:
        print(f"[Voice] VC接続エラー: {type(e).__name__}: {e}")

        voice_client = interaction.guild.voice_client

        if voice_client is not None:
            try:
                await voice_client.disconnect(force=True)
            except Exception:
                pass

        await interaction.followup.send(
            f"❌ ボイスチャンネルへの接続に失敗しました。\n"
            f"`{type(e).__name__}: {e}`",
            ephemeral=True
        )


async def leave_vc(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if interaction.guild is None:
        await interaction.followup.send(
            "❌ サーバー内で実行してください。",
            ephemeral=True
        )
        return

    voice_client = interaction.guild.voice_client

    if voice_client is None:
        await interaction.followup.send(
            "❌ 現在ボイスチャンネルに参加していません。",
            ephemeral=True
        )
        return

    channel_name = (
        voice_client.channel.name
        if voice_client.channel is not None
        else "ボイスチャンネル"
    )

    try:
        await voice_client.disconnect(force=True)

        await interaction.followup.send(
            f"👋 **{channel_name}** から退出しました。",
            ephemeral=True
        )

    except Exception as e:
        print(f"[Voice] VC退出エラー: {type(e).__name__}: {e}")

        await interaction.followup.send(
            f"❌ VCからの退出に失敗しました。\n"
            f"`{type(e).__name__}: {e}`",
            ephemeral=True
        )
