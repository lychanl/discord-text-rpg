from dtrpg.data.locale import LocalizedObject, LocalizedObjectFactory


class GameObject(LocalizedObject):
    def __init__(self):
        super().__init__()
        self.variable_properties = {}
        self.variables = {}

    def add_variable_property(self, name: str, variable: str):
        self.variable_properties[name] = variable

    def set_variable(self, variable: str, value: object):
        self.variables[variable] = value

    def __getattribute__(self, name: str) -> object:
        if name not in ('variable_properties', 'variables')\
                and not name.startswith('_') and name in self.variable_properties:
            return self.variables.get(self.variable_properties[name], None)

        return super().__getattribute__(name)


class GameObjectFactory(LocalizedObjectFactory):
    def __init__(self, clss: type):
        super().__init__(clss)
        self.variable_properties = {}
        self.default_variables = {}

    def add_variable_property(self, name: str, variable: str):
        self.variable_properties[name] = variable

    def _create(self, *args: list, **kwargs: dict):
        obj = super()._create(*args, **kwargs)

        obj.variable_properties = dict(self.variable_properties)
        obj.variables = dict(self.default_variables)

        return obj
