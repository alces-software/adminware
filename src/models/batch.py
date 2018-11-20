
import re
from sqlalchemy import Column, String

from database import Base
from models.config import Config
from models.job import Job
from models.shell_variable import ShellVariable

class Batch(Base):


    config = Column(String)


    def _init_or_load(self):
        self.config_model = Config(self.config)

    def name(self):
        return self.config_model.name()

    def help(self):
        return self.config_model.help()

    def command(self):
        var_models = self.shell_variables
        var_map = map(lambda v: '='.join([v.key, v.value]), var_models)
        var_str = ' && '.join(var_map)
        cmd = self.config_model.command()
        # replace any instances of the variable in cmd with the lowercase
        for variable in [var_model.key for var_model in var_models]:
            matches = re.findall(variable, cmd, re.IGNORECASE)
            for match in matches:
                cmd = re.sub(match, variable, cmd)
        if var_str: cmd = ' && '.join([var_str, cmd])
        return cmd

    def command_exists(self):
        return self.config_model.command_exists()

    def is_interactive(self):
        return self.config_model.interactive()

    def build_jobs(self, *nodes):
        return list(map(lambda n: Job(node = n, batch = self), nodes))

    def build_shell_variables(self, **variables):
        def build(key):
            args = { 'key': key, 'value': variables[key], 'batch': self }
            return ShellVariable(**args)

        return list(map(lambda k: build(k), variables.keys()))
