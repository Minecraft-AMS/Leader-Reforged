import json
import os

from mcdreforged.api.all import *

leaders = []
config = {"max_leaders": 1024}


def leader(server: ServerInterface, executor: str, player: str = None):
    global leaders, config
    controlled = False if player is None or executor == player else True
    if not controlled:
        player = executor
    # !!! 此处缺少在线玩家检测 等待更好的方法
    if player not in leaders:
        if len(leaders) >= config["max_leaders"]:
            server.tell(
                executor,
                RText(
                    server.rtr("leader_reforged.error.max_limit_reached"), RColor.red
                ),
            )
            server.tell(
                executor,
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
            server.tell(
                executor,
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
            server.tell(
                executor,
                RText(
                    server.rtr("leader_reforged.usage.unmark", player),
                    RColor.green,
                    RStyle.italic,
                ),
            )


def on_load(server: PluginServerInterface, old):
    global config
    try:
        with open(os.path.join(server.get_data_folder(), "config.json"), "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        with open(os.path.join(server.get_data_folder(), "config.json"), "w") as file:
            json.dump(config, file)
    server.register_command(
        Literal("!!leader")
        .requires(lambda src: src.is_player)
        .runs(lambda src: leader(server, src.player))
        .then(
            Text("player").runs(
                lambda src, ctx: leader(server, src.player, ctx["player"])
            )
        )
    )
    server.register_help_message(
        "!!leader", server.rtr("leader_reforged.plugin.help_message")
    )
