import json
import os

from mcdreforged.api.all import *


class Leader(list):

    """
    The base class of Leader-Reforged.
    """

    # Logger Part

    class Logger:

        """
        The logging class of Leader-Reforged.
        """

        class LogStyles:

            """
            The style presets of Leader-Reforged's logging class.
            """

            INFO = [RColor.white]
            ERROR = [RColor.red]

        def say(styles: LogStyles()):

            """
            A decorator which prints styled and translatable message to someone.
            """

            def inner(func):
                def wrapper(*args, **kwargs):
                    _, __ = func(*args, **kwargs), ServerInterface.get_instance()
                    __.tell(_[0], RText(__.rtr(**_[1]), *styles))
                    return

                return wrapper

            return inner

        def shout(styles: LogStyles()):

            """
            A decorator which prints styled and translatable message to everyone.
            """

            def inner(func):
                def wrapper(*args, **kwargs):
                    _, __ = func(*args, **kwargs), ServerInterface.get_instance()
                    __.say(RText(__.rtr(**_), *styles))
                    return

                return wrapper

            return inner

        @say(LogStyles.INFO)
        def help_line(self, executor: str, line: int) -> list:
            return [
                executor,
                {"translation_key": f"leader_reforged.plugin.help_line.{line}"},
            ]

        @shout(LogStyles.INFO)
        def mark(self, player: str) -> dict:
            return {"translation_key": "leader_reforged.info.mark", "player": player}

        @shout(LogStyles.INFO)
        def unmark(self, player: str) -> dict:
            return {"translation_key": "leader_reforged.info.unmark", "player": player}

        @say(LogStyles.INFO)
        def all_leaders(self, executor: str, leaders: list) -> list:
            return (
                [
                    executor,
                    {
                        "translation_key": "leader_reforged.info.all_leaders",
                        "now": leaders.__len__(),
                        "maximum": "∞"
                        if leaders.config["max_leaders"] <= 0
                        else leaders.config["max_leaders"],
                        "players": " ".join(leaders),
                    },
                ]
                if leaders
                else [executor, {"translation_key": "leader_reforged.info.no_leader"}]
            )

        @say(LogStyles.ERROR)
        def player_exists(self, executor, player) -> list:
            return [
                executor,
                {
                    "translation_key": "leader_reforged.error.player_exists",
                    "player": player,
                },
            ]

        @say(LogStyles.ERROR)
        def player_not_exists(self, executor, player) -> list:
            return [
                executor,
                {
                    "translation_key": "leader_reforged.error.player_not_exists",
                    "player": player,
                },
            ]

        @say(LogStyles.ERROR)
        def max_limit_exceeded(self, executor) -> list:
            return [
                executor,
                {"translation_key": "leader_reforged.error.max_limit_exceeded"},
            ]

    logger = Logger()

    # Configuration Part

    def load_config(self, server: PluginServerInterface) -> None:

        """
        Loads configuration file from `config/leader_reforged/config.json` if there is one.\n
        Otherwise, initilize a default configuration file at that place.
        """

        try:
            with open(
                os.path.join(server.get_data_folder(), "config.json"), "r"
            ) as file:
                self.config = json.load(file)
        except FileNotFoundError:
            with open(
                os.path.join(server.get_data_folder(), "config.json"), "w"
            ) as file:
                json.dump(self.config, file)
        return

    def is_maxed(self) -> bool:

        """
        Determines whether the the amount of leaders is at maximum or not.
        """

        return (
            False
            if self.config["max_leaders"] <= 0
            else self.__len__() >= self.config["max_leaders"]
        )

    config = {"max_leaders": 0}

    # Implement Part

    @staticmethod
    def give_effect(player: str) -> None:

        """
        Gives glowing effect to specified player.
        """

        return ServerInterface.get_instance().execute(
            f"/effect give {player} minecraft:glowing 86400 0 true"
        )

    @staticmethod
    def clear_effect(player: str) -> None:

        """
        Clears glowing effect from specified player.
        """

        return ServerInterface.get_instance().execute(
            f"/effect clear {player} minecraft:glowing"
        )

    # Avaliavle methods

    def help_menu(self, executor: str) -> None:
        for line in range(4):
            self.logger.help_line(executor, line)

    def append(self, executor: str, player: str = None) -> None:

        """
        Overrides `list.append()`.\n
        Now also processes plugin works.
        """

        if player is None:
            player = executor
        if player in self.__iter__():
            self.logger.player_exists(executor, player)
            return
        elif self.is_maxed():
            self.logger.max_limit_exceeded(executor)
            return
        self.give_effect(player)
        self.logger.mark(player)
        return super().append(player)

    def remove(self, executor: str, player: str = None) -> None:

        """
        Overrides `list.remove()`.\n
        Now also processes plugin works.
        """

        if player is None:
            player = executor
        if player not in self.__iter__():
            self.logger.player_not_exists(executor, player)
            return
        self.clear_effect(player)
        self.logger.unmark(player)
        return super().remove(player)

    def __str__(self, executor: str) -> str:
        return self.logger.all_leaders(executor, self)

    def __init__(self, server: PluginServerInterface = None) -> None:
        if server is not None:
            return self.load_config(server)


leader = Leader()  # Wait for `on_load()`


# MCDReforged Events


def on_load(server: PluginServerInterface, old):
    global leader
    leader = Leader(server)
    server.register_command(
        Literal("!!leader")
        .requires(lambda src: src.is_player)
        .runs(lambda src: leader.help_menu(src.player))
        .then(
            Literal("+")
            .runs(lambda src: leader.append(src.player))
            .then(
                Text("player").runs(
                    lambda src, ctx: leader.append(src.player, ctx["player"])
                )
            )
        )
        .then(
            Literal("-")
            .runs(lambda src: leader.remove(src.player))
            .then(
                Text("player").runs(
                    lambda src, ctx: leader.remove(src.player, ctx["player"])
                )
            )
        )
        .then(Literal("?").runs(lambda src: leader.__str__(src.player)))
    )
    server.register_help_message(
        "!!leader", server.rtr("leader_reforged.plugin.help_message")
    )
