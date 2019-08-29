
class ControllerGenerator():

    """
    Register class to provide a decorator that is used to go through the package and
    register available scenes.
    """

    subclasses = {}

    @classmethod
    def register_subclass(cls, controller_type):
        def decorator(subclass):
            cls.subclasses[controller_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):

        controller_type = params.get('type', None)

        if controller_type is None:
            raise ValueError('Controller not selected')

        if controller_type not in cls.subclasses:
            raise ValueError('Controller not implemented: ' + controller_type)

        return cls.subclasses[controller_type](params)


class Controller():

    def __init__(self):

        self.require_key_mapping = False
        self.available_actions = {}
        self.actions = {}

    def get_actions(self):
        pass

    def set_available_actions(self, available_actions):
        pass
