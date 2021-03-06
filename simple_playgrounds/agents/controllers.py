"""
Module defining Controllers.
Controllers are used to generate commands to control the actuators of an agent.
"""
from abc import ABC, abstractmethod
import random

import pygame

from simple_playgrounds.utils.definitions import ActionTypes, KeyTypes


class Controller(ABC):
    """ Base Class for Controllers.
    """

    def __init__(self):

        self.require_key_mapping = False
        self.controlled_actuators = []

    @abstractmethod
    def generate_commands(self):
        """ Generate actions for each part of an agent,
        Returns a dictionary of parts and associated actions,
        """

    def generate_empty_commands(self):
        commands = {}
        for actuator in self.controlled_actuators:
            commands[actuator] = 0

        return commands


class External(Controller):

    def generate_commands(self):
        pass


class Random(Controller):
    """
    A random controller generate random commands.
    If the actuator is continuous, it picks the action using a uniform distribution.
    If the actuator is discrete (binary), it picks a random action.
    """
    controller_type = 'random'

    def generate_commands(self):

        # actions = self.null_actions.copy()
        commands = {}

        for actuator in self.controlled_actuators:

            if actuator.action_type == ActionTypes.CONTINUOUS_CENTERED:
                act_value = random.uniform(actuator.min, actuator.max)

            elif actuator.action_type == ActionTypes.CONTINUOUS_NOT_CENTERED:
                act_value = random.uniform(actuator.min, actuator.max)

            elif actuator.action_type == ActionTypes.DISCRETE:
                act_value = random.choice([actuator.min, actuator.max])

            else:
                raise ValueError

            commands[actuator] = act_value

        return commands


class Keyboard(Controller):
    """
    Keyboard controller require that a keymapping is defined in the agent.
    The keymapping should be assigned to the controller.
    """
    controller_type = 'keyboard'

    def __init__(self):

        super().__init__()

        self.require_key_mapping = True
        self.key_map = None

        self.press_once = []
        self.press_hold = []

        self.hold = []

    def discover_key_mapping(self):
        """ Key mapping that links keyboard strokes with a desired action."""

        self.key_map = {}

        for actuator in self.controlled_actuators:

            if actuator.has_key_mapping:

                for key, (behavior, value) in actuator.key_map.items():

                    if key in self.key_map:
                        raise ValueError("Key assigned twice")

                    self.key_map[key] = (actuator, behavior, value)

    def generate_commands(self):

        # pylint: disable=undefined-variable

        all_key_pressed = pygame.key.get_pressed()

        pressed = []
        for key, _ in self.key_map.items():
            if all_key_pressed[key] == 1:
                pressed.append(key)

        for key_pressed in self.press_hold:
            if key_pressed not in pressed:
                self.press_hold.remove(key_pressed)

        for key_pressed in self.press_once:
            if key_pressed not in pressed:
                self.press_once.remove(key_pressed)

        commands = self.generate_empty_commands()

        for key_pressed in pressed:

            actuator, behavior, value = self.key_map[key_pressed]

            if behavior == KeyTypes.PRESS_HOLD:
                commands[actuator] = value

                if key_pressed not in self.press_hold:
                    self.press_hold.append(key_pressed)

            if behavior == KeyTypes.PRESS_ONCE and key_pressed not in self.press_once:
                commands[actuator] = value
                self.press_once.append(key_pressed)

        return commands
