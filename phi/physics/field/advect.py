from phi.physics.field import SampledField
from .field import StaggeredSamplePoints, Field


def semi_lagrangian(field, velocity_field, dt):
    """
Semi-Lagrangian advection with simple backward lookup.
        :param field: Field to be advected
        :param velocity_field: Field, need not be compatible with field.
        :param dt: time step
        :return: Field compatible with input field
    """
    try:
        x0 = field.points
        v = velocity_field.at(x0)
        x = x0 - v * dt
        data = field.sample_at(x.data)
        return field.with_data(data)
    except StaggeredSamplePoints:
        advected = [semi_lagrangian(component, velocity_field, dt) for component in field.unstack()]
        return field.with_data(advected)


def runge_kutta_4(field, velocity, dt):
    """
Lagrangian advection of particles.
    :param field: SampledField with any number of components
    :type field: SampledField
    :param velocity: Vector field
    :type velocity: Field
    :param dt: time step
    :return: SampledField with same data as `field` but advected points
    """
    assert isinstance(field, SampledField)
    assert isinstance(velocity, Field)
    points = field.points
    # --- Sample velocity at intermediate points ---
    vel_k1 = velocity.at(points)
    vel_k2 = velocity.at(points + 0.5 * dt * vel_k1)
    vel_k3 = velocity.at(points + 0.5 * dt * vel_k2)
    vel_k4 = velocity.at(points + dt * vel_k3)
    # --- Combine points with RK4 scheme ---
    new_points = points + dt * (1/6.) * (vel_k1 + 2 * (vel_k2 + vel_k3) + vel_k4)
    result = SampledField(new_points.data, field.data, mode=field.mode, point_count=field._point_count)
    return result
