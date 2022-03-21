import json
from mcdreforged.api.all import *
import os

leaders = []
players = []
config = {"max_leaders": 1024}


def leader(server: ServerInterface, info: Info, player: str = None):
    global leaders, players, config
    controlled = False
    if player is None:
        player = info.player
    else:
        # 临时取消了玩家识别 等待更好的方案
        # if player not in players:
        #     server.reply(info, RText(server.rtr("leader_reforged.error.player_not_found"), RColor.red))
        #     return
        controlled = True
    if info.player == player:
        controlled = False
    if player not in leaders:
        if len(leaders) >= config["max_leaders"]:
            server.reply(
                info,
                RText(
                    server.rtr("leader_reforged.error.max_limit_reached"), RColor.red
                ),
            )
            server.reply(
                info,
                RText(
                    server.rtr("leader_reforged.usage.leaders", " ".join(leaders)),
                    RColor.red,
                ),
            )
            return
        leaders.append(player)
        server.execute(f"/effect give {player} minecraft:glowing 86400 0 true")
        server.tell(
            player,
            RText(
                server.rtr("leader_reforged.usage.being_marked"),
                RColor.green,
                RStyle.italic,
            ),
        )
        if controlled:
            server.reply(
                info,
                RText(
                    server.rtr("leader_reforged.usage.mark", player),
                    RColor.green,
                    RStyle.italic,
                ),
            )
    else:
        leaders.remove(player)
        server.execute(f"/effect clear {player} minecraft:glowing")
        server.tell(
            player,
            RText(
                server.rtr("leader_reforged.usage.being_unmarked"),
                RColor.green,
                RStyle.italic,
            ),
        )
        if controlled:
            server.reply(
                info,
                RText(
                    server.rtr("leader_reforged.usage.unmark", player),
                    RColor.green,
                    RStyle.italic,
                ),
            )


def on_user_info(server: PluginServerInterface, info: Info):
    raw_command = info.content.split()
    if raw_command[0] == "!!leader":
        if len(raw_command) == 1:
            leader(server, info)
        elif len(raw_command) == 2:
            leader(server, info, raw_command[1])
        else:
            server.reply(
                info, RText(server.rtr("leader_reforged.error.usage"), RColor.red)
            )


def on_load(server: PluginServerInterface, old):
    global config
    try:
        with open(os.path.join(server.get_data_folder(), "config.json"), "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        with open(os.path.join(server.get_data_folder(), "config.json"), "w") as file:
            json.dump(config, file)
    server.register_help_message(
        "!!leader", server.rtr("leader_reforged.plugin.help_message")
    )


# def on_player_joined(server: PluginServerInterface, player: str, info: Info):
#     global players
#     players.append(player)
#
# def on_player_left(server: PluginServerInterface, player: str):
#     global players
#     try:
#         players.remove(player)
#     except Exception:
#         pass
