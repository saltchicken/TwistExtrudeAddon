"""Core generation math and B-Rep solid construction engine."""

import math

import FreeCAD as App
import Part

from freecad.twistextrude.config import TwistConfig


def get_twist_t(t, twist_easing):
    """Calculates the eased value of 't' for the twist angle."""
    if twist_easing == "Ease In (Quad)":
        return t * t
    elif twist_easing == "Ease Out (Quad)":
        return 1.0 - (1.0 - t) * (1.0 - t)
    elif twist_easing == "Ease In-Out (Smoothstep)":
        return t * t * (3.0 - 2.0 * t)
    elif twist_easing == "Ease In-Out (Sine)":
        return 0.5 * (1.0 - math.cos(math.pi * t))
    return t


def generate_twist_shape(profile_obj, path_obj, config: TwistConfig):
    """
    Calculates and returns the resulting FreeCAD Shape of the twist extrusion.
    Does not create or mutate parametric FreeCAD objects.
    """
    if not profile_obj or not hasattr(profile_obj, "Shape"):
        return Part.makeCompound([])

    is_path_mode = False
    points, tangents = [], []

    if path_obj and hasattr(path_obj, "Shape") and len(
            path_obj.Shape.Wires) > 0:
        is_path_mode = True
        path_wire = path_obj.Shape.Wires[0]
        points = path_wire.discretize(Number=config.num_sections)

        for i in range(config.num_sections):
            if i == 0:
                t_vec = points[1] - points[0]
            elif i == config.num_sections - 1:
                t_vec = points[-1] - points[-2]
            else:
                t_vec = points[i + 1] - points[i - 1]
            t_vec.normalize()
            tangents.append(t_vec)

    if config.num_sections < 2:
        return Part.makeCompound([])

    base_shape = profile_obj.Shape
    if not base_shape.Wires:
        return Part.makeCompound([])

    base_wire = base_shape.Wires[0].copy()
    section_wires = []

    safe_env = {
        "math": math,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
        "pow": pow,
        "abs": abs,
        "sqrt": math.sqrt,
        "log": math.log
    }

    for i in range(config.num_sections):
        t = float(i) / (config.num_sections - 1)
        twist_t = get_twist_t(t, config.twist_easing)

        angle = twist_t * config.total_angle
        z = t * config.total_height if not is_path_mode else 0.0

        local_env = safe_env.copy()
        local_env["t"] = t
        local_env["z"] = z

        try:
            scale_factor = eval(config.equation_str, {"__builtins__": {}},
                                local_env)
            scale_factor = max(0.001, float(scale_factor))
        except Exception:
            scale_factor = 1.0  # Gracefully degrade on syntax errors while typing

        if is_path_mode:
            point = points[i]
            tangent = tangents[i]
            z_vec = App.Vector(0, 0, 1)

            if z_vec.dot(tangent) < -0.9999:
                align_rot = App.Rotation(App.Vector(1, 0, 0), 180)
            elif z_vec.dot(tangent) > 0.9999:
                align_rot = App.Rotation(0, 0, 0)
            else:
                align_rot = App.Rotation(z_vec, tangent)

            twist_rot = App.Rotation(App.Vector(0, 0, 1), angle)
            final_rot = align_rot.multiply(twist_rot)
            new_placement = App.Placement(point, final_rot)
        else:
            new_placement = App.Placement(
                App.Vector(0, 0, z), App.Rotation(App.Vector(0, 0, 1), angle))

        # Apply transformation to the wire
        mat = new_placement.Matrix
        scale_mat = App.Matrix()
        scale_mat.scale(scale_factor, scale_factor, scale_factor)
        final_mat = mat.multiply(scale_mat)

        w = base_wire.copy()
        w = w.transformShape(final_mat)
        section_wires.append(w)

    if config.sketches_only:
        return Part.makeCompound(section_wires)
    else:
        try:
            solid = True if base_shape.isClosed() else False
            return Part.makeLoft(section_wires, solid)
        except Exception:
            return Part.makeCompound(section_wires)
