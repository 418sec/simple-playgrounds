import pymunk, math, pygame, random

from .entity import  Entity
from utils import pygame_utils
from utils.config import *


class ActionableObject(Entity):

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """
        super(ActionableObject, self).__init__()

        # Create shape, the body is static

        self.physical_shape = params['physical_shape']
        self.movable = params['movable']
        self.position = params['position']

        self.action_radius = params['action_radius']
        self.actionable_type = params['actionable_type']

        self.params = params


        self.name_id = self.actionable_type + '_'+str(EdibleObject.id_number)




        if self.physical_shape == 'circle':
            self.radius = params['radius']

        elif self.physical_shape == 'box':
            self.size_box = params['size_box']

        elif self.physical_shape == 'poly':
            self.vertices = params['vertices']


        if self.movable:
            self.mass = params['mass']
            inertia = self.compute_moments()
            self.body_body = pymunk.Body(self.mass, inertia)

        else:
            self.mass = None
            self.body_body = pymunk.Body(body_type=pymunk.Body.STATIC)

        self.body_body.position = params['position'][0:2]
        self.body_body.angle = params['position'][2]

        shape_body, shape_sensor = self.generate_pymunk_shape( self.body_body )

        self.shape_body = shape_body
        self.shape_body.friction = 1.
        self.shape_body.elasticity = 0.95


        if 'default_color' in params:
            self.shape_body.color = params['default_color']

        self.shape_sensor = shape_sensor

        self.body_sensor = self.body_body.copy()

        self.shape_body.collision_type = collision_types['basic_object']


    def actionate(self):

        print('Is actionated')


    def generate_pymunk_shape(self, body):


        if self.physical_shape == 'circle':

            shape_body = pymunk.Circle(body, self.radius)
            shape_sensor = pymunk.Circle(body, self.radius + self.action_radius)

            shape_sensor.sensor = True
        #elif self.physical_shape == 'poly':

        #    shape = pymunk.Poly(body, self.vertices)

        #elif self.physical_shape == 'box':

        #    shape = pymunk.Poly.create_box(body, self.size_box)

        else:

            raise ValueError('Not implemented')

        return shape_body, shape_sensor



    def compute_moments(self):

        if self.physical_shape == 'circle':

            moment = pymunk.moment_for_circle(self.mass, 0, self.radius)

        elif self.physical_shape == 'poly':

            moment = pymunk.moment_for_poly(self.mass, self.vertices)

        elif self.physical_shape == 'box':

            moment =  pymunk.moment_for_box(self.mass, self.size_box)

        else:

            raise ValueError('Not implemented')

        return moment


    def draw(self, surface):
        """
        Draw the obstacle on the environment screen
        """
        pass
    #
    #     if self.appearance == 'rectangle':
    #
    #         # Rotate and center the texture
    #
    #         texture_surface = pygame.transform.rotate(self.texture, self.theta * 180/math.pi)
    #         texture_surface_rect = texture_surface.get_rect()
    #         texture_surface_rect.center = pygame_utils.to_pygame((self.x, self.y), surface)
    #
    #         # Blit the masked texture on the screen
    #         surface.blit(texture_surface, texture_surface_rect, None)



class ActionableGenerator():

    subclasses = {}

    @classmethod
    def register_subclass(cls, actionable_type):
        def decorator(subclass):
            cls.subclasses[actionable_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):
        actionable_type = params['actionable_type']
        if actionable_type not in cls.subclasses:
            #TODO: verify rais eerroe?
            raise ValueError('Entity type not implemented:' + actionable_type)

        return cls.subclasses[actionable_type](params)


@ActionableGenerator.register_subclass('distractor')
class DistractorObject(ActionableObject):

    def __init__(self, params):

        super(DistractorObject, self).__init__(params)

        self.shape_sensor.collision_type = collision_types['activable']


    def actionate(self):

        self.shape_body.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


@ActionableGenerator.register_subclass('edible')
class EdibleObject(ActionableObject):

    def __init__(self, params):

        super(EdibleObject, self).__init__(params)

        self.shrink_when_eaten = params['shink_when_eaten']

        self.shape_sensor.collision_type = collision_types['edible']

        self.reward = params.get('initial_reward', 0)



    def actionate(self):

        self.radius = self.shrink_when_eaten * self.radius
        self.reward = self.shrink_when_eaten * self.reward


        if self.movable:
            self.mass = self.shrink_when_eaten * self.mass
            inertia = self.compute_moments()
            body = pymunk.Body(self.mass, inertia)

        else:
            self.mass = None
            body = pymunk.Body(body_type=pymunk.Body.STATIC)

        body.position = self.body_body.position
        body.angle = self.body_body.angle

        self.body_body = body
        shape_body, shape_sensor = self.generate_pymunk_shape( self.body_body )

        self.shape_body = shape_body
        self.shape_body.friction = 1.
        self.shape_body.elasticity = 0.95


        if 'default_color' in self.params:
            self.shape_body.color = self.params['default_color']
        #
        self.shape_sensor = shape_sensor

        self.shape_sensor.collision_type = collision_types['edible']
        #
        self.body_sensor = self.body_body.copy()
        #


@ActionableGenerator.register_subclass('dispenser')
class DispenserObject(ActionableObject):

    def __init__(self, params):

        super(DispenserObject, self).__init__(params)

        self.shape_sensor.collision_type = collision_types['activable']

        self.object_produced = params['object']

        self.production_area_shape = params['area_shape']
        self.production_area = params['area']

        self.limit = params['limit']


    def actionate(self):

        obj = self.object_produced

        if self.production_area_shape == 'rectangle':

            x = random.uniform( self.production_area[0][0],self.production_area[1][0] )
            y = random.uniform( self.production_area[0][1],self.production_area[1][1] )

            obj['position'] = (x,y,0)

        return obj

@ActionableGenerator.register_subclass('graspable')
class GraspableObject(ActionableObject):

    def __init__(self, params):

        super(GraspableObject, self).__init__( params)

        self.shape_sensor.collision_type = collision_types['graspable']

        self.graspable = True

    def actionate(self):
        pass



@ActionableGenerator.register_subclass('door')
class DoorObject(ActionableObject):

    def __init__(self, params):

        super(DoorObject, self).__init__(params)

        self.shape_sensor.collision_type = collision_types['activable']

        self.door_params = params['door']

        self.time_open = params['time_open']

        self.door_closed = True

    def actionate(self):

        obj = self.object_produced

        if self.production_area_shape == 'rectangle':

            x = random.uniform( self.production_area[0][0],self.production_area[1][0] )
            y = random.uniform( self.production_area[0][1],self.production_area[1][1] )

            obj['position'] = (x,y,0)

        return obj


