
import click


class Action:
    def __init__(self, config):
        self.config = config

    def create(self, click_group, command_func):
        def action_func(arguments):
            return command_func(self.config, arguments)
        action_func.__name__ = self.config.__name__()
        action_func = self.__click_command(action_func, click_group)

    def __click_command(self, func, click_group):
        return click.argument('arguments', nargs=-1)(click_group.command(help=self.config.help())(func))


class ActionFamily:
    configs = []

    def __init__(self, name):
        self.name = name

    def set_configs(configs):
        ActionFamily.configs = configs

    def get_members_configs(self):
        members_configs = []
        for config in ActionFamily.configs:
            if self.name in config.families():
                members_configs += [config]
        return members_configs

    def create(self, click_group, command_func):
        def action_family_func():
            return command_func(self.name, self.get_members_configs())
        action_family_func.__name__ = self.name
        action_family_func = click_group.command(
             help='Run the command family \'{}\''.format(self.name)
             )(action_family_func)
