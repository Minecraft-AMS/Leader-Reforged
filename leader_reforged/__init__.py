from mcdreforged.api.all import *

LANGUAGE = {
    "en_us": {
        "mark": "{} is now a leader.",
        "unmark": "{} is now no longer a leader.",
        "being_marked": "You are now a leader.",
        "being_unmarked": "You are now no longer a leader.",
        "command_error": "Unknown usage.",
        "player_not_found_error": "Player not found.",
        "help_message": "Marks a leader."
    },
    "zh_cn": {
        "mark": "{} 成为导游了。",
        "unmark": "{} 不再是导游了。",
        "being_marked": "你成为导游了。",
        "being_unmarked": "你不再是导游了。",
        "command_error": "未知用法。",
        "player_not_found_error": "未找到玩家。",
        "help_message": "选择是否成为导游。"
    }
}

leaders = []
players = []

try:
    lang = LANGUAGE[ServerInterface.get_instance().get_mcdr_language()]
except Exception:
    lang = LANGUAGE["en_us"]

def leader(server: ServerInterface, info: Info, player: str = None):
    global leaders, players, lang
    controlled = False
    if player is None:
        player = info.player
    else:
        if player not in players:
            server.reply(info, RText(lang["player_not_found_error"], RColor.red))
            return
        controlled = True
    if info.player == player:
        controlled = False
    if player not in leaders:
        leaders.append(player)
        server.execute(f"/effect give {player} minecraft:glowing 86400 0 true")
        server.tell(player, RText(lang["being_marked"], RColor.green, RStyle.italic))
        if controlled:
            server.reply(info, RText(lang["mark"].format(player), RColor.green, RStyle.italic))
    else:
        leaders.remove(player)
        server.execute(f"/effect clear {player} minecraft:glowing")
        server.tell(player, RText(lang["being_unmarked"], RColor.green, RStyle.italic))
        if controlled:
            server.reply(info, RText(lang["unmark"].format(player), RColor.green, RStyle.italic))

def on_user_info(server: PluginServerInterface, info: Info):
    raw_command = info.content.split()
    if raw_command[0] == "!!leader":
        if len(raw_command) == 1:
            leader(server, info)
        elif len(raw_command) == 2:
            leader(server, info, raw_command[1])
        else:
            server.reply(info, RText(lang["command_error"], RColor.red))

def on_load(server: PluginServerInterface, old):
    global lang
    server.register_help_message("!!leader", lang["help_message"])

def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    global players
    players.append(player)

def on_player_left(server: PluginServerInterface, player: str):
    global players
    try:
        players.remove(player)
    except Exception:
        pass