import numpy
from typing import Collection


class Hailstone:
    def __init__(self, data) -> None:
        self.load(data)

    def __str__(self) -> str:
        return repr(self.origin) + repr(self.velocity)

    def position(self, t=0.0):
        """
        Return the position at time t.
        """
        return self.origin + t * self.velocity

    def load(self, data):
        """
        Load hailstone data in the format "sx, sy, sz @ vx, xy, vz", where s is the origin and v the velocity.
        """
        [origin, velocity] = data.split("@")
        self.origin = numpy.asarray(origin.split(", "), dtype=float)
        self.velocity = numpy.asarray(velocity.split(", "), dtype=float)

    def collide_xy(self, other: "Hailstone"):
        """
        Returns the location and time of the point where two Hail's paths cross in the xy dimension.
        """
        # general equations of hail paths
        #   position1 = self.origin + t1 * self.velocity
        #   position2 = other.origin + t2 * other.velocity
        # intersect when position1 == position2
        #   self.origin + t1 * self.velocity = other.origin + t2 * other.velocity
        # separate into separate dimensions
        #   self.origin[0] + t1 * self.velocity[0] = other.origin[0] + t2 * other.velocity[0]
        #   self.origin[1] + t1 * self.velocity[1] = other.origin[1] + t2 * other.velocity[1]
        # rearrange y to get t2
        #   t2 = (self.origin[1] - other.origin[1] + t1 * self.velocity[1]) / other.velocity[1]
        # substitute into x
        #   self.origin[0] + t1 * self.velocity[0] = other.origin[0] + ((self.origin[1] - other.origin[1] + t1 * self.velocity[1]) / other.velocity[1]) * other.velocity[0]
        # rearrange
        #   t1 * self.velocity[0] = (other.origin[0] - self.origin[0]) + ((self.origin[1] - other.origin[1] + t1 * self.velocity[1]) * other.velocity[0] / other.velocity[1])
        #   t1 * self.velocity[0] = (other.origin[0] - self.origin[0]) + (self.origin[1] - other.origin[1]) * other.velocity[0] / other.velocity[1] + t1 * self.velocity[1] * other.velocity[0] / other.velocity[1]
        #   t1 * self.velocity[0] - t1 * self.velocity[1] * other.velocity[0] / other.velocity[1] = (other.origin[0] - self.origin[0]) + (self.origin[1] - other.origin[1]) * other.velocity[0] / other.velocity[1]
        #   t1 * (self.velocity[0] - self.velocity[1] * other.velocity[0] / other.velocity[1]) = (other.origin[0] - self.origin[0]) + (self.origin[1] - other.origin[1]) * other.velocity[0] / other.velocity[1]
        with numpy.errstate(divide="ignore"):
            t1 = (
                (other.origin[0] - self.origin[0])
                + (self.origin[1] - other.origin[1])
                * other.velocity[0]
                / other.velocity[1]
            ) / (
                self.velocity[0]
                - self.velocity[1] * other.velocity[0] / other.velocity[1]
            )
            t2 = (
                self.origin[1] - other.origin[1] + t1 * self.velocity[1]
            ) / other.velocity[1]
        collision = self.position(t1)
        return collision[:2], t1, t2


def find_rock(hail):
    # the rock position is given by the formula
    #   xyz = rock.origin + t * rock.velocity

    # xyzN is the position of hailstone N
    #   xyzN = hail[N].origin + tN * hail[N].velocity

    # the vector from hailstone N to the rock is given by
    #   xyzNr = xyzN - xyz
    #   xyzNr = hail[N].origin + tN * hail[N].velocity - rock.origin - t * rock.velocity

    # at the intersection tN = t and xyzNr = 0
    #   0 = hail[N].origin + tN * hail[N].velocity - rock.origin - tN * rock.velocity
    #   0 = hail[N].origin - rock.origin + tN * (hail[N].velocity - rock.velocity)
    #   tN = (rock.origin - hail[N].origin)/(hail[N].velocity - rock.velocity)

    # considering the xyz components
    #   tN = (rock.origin[0] - hail[N].origin[0])/(hail[N].velocity[0] - rock.velocity[0])
    #   tN = (rock.origin[1] - hail[N].origin[1])/(hail[N].velocity[1] - rock.velocity[1])
    #   tN = (rock.origin[2] - hail[N].origin[2])/(hail[N].velocity[2] - rock.velocity[2])

    # rearrange to remove t0
    #     (rock.origin[0] - hail[N].origin[0])/(hail[N].velocity[0] - rock.velocity[0])
    #   = (rock.origin[1] - hail[N].origin[1])/(hail[N].velocity[1] - rock.velocity[1])
    #   = (rock.origin[2] - hail[N].origin[2])/(hail[N].velocity[2] - rock.velocity[2])

    # rearrange
    #   (rock.origin[0] - hail[N].origin[0])*(hail[N].velocity[1] - rock.velocity[1]) = (rock.origin[1] - hail[N].origin[1])*(hail[N].velocity[0] - rock.velocity[0])
    # expand
    #     rock.origin[0] * hail[N].velocity[1] - rock.origin[0] * rock.velocity[1] - hail[N].origin[0] * hail[N].velocity[1] + hail[N].origin[0] * rock.velocity[1])
    #   = rock.origin[1] * hail[N].velocity[0] - rock.origin[1] * rock.velocity[0] - hail[N].origin[1] * hail[N].velocity[0] + hail[N].origin[1] * rock.velocity[0]

    # subtract hailstone 0
    #     rock.origin[0] * hail[N].velocity[1] - rock.origin[0] * rock.velocity[1] - hail[N].origin[0] * hail[N].velocity[1] + hail[N].origin[0] * rock.velocity[1]
    #   - rock.origin[0] * hail[0].velocity[1] + rock.origin[0] * rock.velocity[1] + hail[0].origin[0] * hail[0].velocity[1] - hail[0].origin[0] * rock.velocity[1]
    #   = rock.origin[1] * hail[N].velocity[0] - rock.origin[1] * rock.velocity[0] - hail[N].origin[1] * hail[N].velocity[0] + hail[N].origin[1] * rock.velocity[0]
    #   - rock.origin[1] * hail[0].velocity[0] + rock.origin[1] * rock.velocity[0] + hail[0].origin[1] * hail[0].velocity[0] - hail[0].origin[1] * rock.velocity[0]

    # cancel out common terms
    #     rock.origin[0] * hail[N].velocity[1] - hail[N].origin[0] * hail[N].velocity[1] + hail[N].origin[0] * rock.velocity[1]
    #   - rock.origin[0] * hail[0].velocity[1] + hail[0].origin[0] * hail[0].velocity[1] - hail[0].origin[0] * rock.velocity[1]
    #   = rock.origin[1] * hail[N].velocity[0] - hail[N].origin[1] * hail[N].velocity[0] + hail[N].origin[1] * rock.velocity[0]
    #   - rock.origin[1] * hail[0].velocity[0] + hail[0].origin[1] * hail[0].velocity[0] - hail[0].origin[1] * rock.velocity[0]

    # collect rock terms
    #     rock.origin[0] * (hail[N].velocity[1] - hail[0].velocity[1])
    #   + rock.origin[1] * (hail[0].velocity[0] - hail[N].velocity[0])
    #   + rock.velocity[0] * (hail[0].origin[1] - hail[N].origin[1])
    #   + rock.velocity[1] * (hail[N].origin[0] - hail[0].origin[0])
    #   = hail[N].origin[0] * hail[N].velocity[1] - hail[0].origin[0] * hail[0].velocity[1]
    #   + hail[0].origin[1] * hail[0].velocity[0] - hail[N].origin[1] * hail[N].velocity[0]

    # equation in the form rock.origin[0]*α + rock.origin[1]*β + rock.velocity[0]*γ + rock.velocity[1]*δ = ε
    # i.e. _A_ * rock_paramaeters = epsilon
    # so:  rock_parameters = _A_.inverse() * epsilon

    # gather 4 terms for the solution for 4 unknowns
    XY = numpy.zeros((4, 4), dtype="double")
    epsilonXY = numpy.zeros((4, 1), dtype="double")

    # repeat analagous calculation for z - swap all indices from [1] -> [2]
    XZ = numpy.zeros((4, 4), dtype="double")
    epsilonXZ = numpy.zeros((4, 1), dtype="double")

    for N in range(1, 5):
        XY[N - 1, 0] = hail[N].velocity[1] - hail[0].velocity[1]
        XY[N - 1, 1] = hail[0].velocity[0] - hail[N].velocity[0]
        XY[N - 1, 2] = hail[0].origin[1] - hail[N].origin[1]
        XY[N - 1, 3] = hail[N].origin[0] - hail[0].origin[0]
        epsilonXY[N - 1] = (
            hail[N].origin[0] * hail[N].velocity[1]
            - hail[0].origin[0] * hail[0].velocity[1]
            + hail[0].origin[1] * hail[0].velocity[0]
            - hail[N].origin[1] * hail[N].velocity[0]
        )

        XZ[N - 1, 0] = hail[N].velocity[2] - hail[0].velocity[2]
        XZ[N - 1, 1] = hail[0].velocity[0] - hail[N].velocity[0]
        XZ[N - 1, 2] = hail[0].origin[2] - hail[N].origin[2]
        XZ[N - 1, 3] = hail[N].origin[0] - hail[0].origin[0]
        epsilonXZ[N - 1] = (
            hail[N].origin[0] * hail[N].velocity[2]
            - hail[0].origin[0] * hail[0].velocity[2]
            + hail[0].origin[2] * hail[0].velocity[0]
            - hail[N].origin[2] * hail[N].velocity[0]
        )

    rock_parametersXY = numpy.round(numpy.asmatrix(XY).getI() * epsilonXY).astype(
        "int64"
    )
    rock_parametersXZ = numpy.round(numpy.asmatrix(XZ).getI() * epsilonXZ).astype(
        "int64"
    )

    # make sure the x value is the same
    assert rock_parametersXY[0, 0] == rock_parametersXZ[0, 0]
    assert rock_parametersXY[2, 0] == rock_parametersXZ[2, 0]

    rock_origin = (
        rock_parametersXY[0, 0],
        rock_parametersXY[1, 0],
        rock_parametersXZ[1, 0],
    )
    rock_velocity = (
        rock_parametersXY[2, 0],
        rock_parametersXY[3, 0],
        rock_parametersXZ[3, 0],
    )

    return rock_origin, rock_velocity


def load(data):
    hail = list()
    for dataline in data:
        if not dataline:
            continue
        hail.append(Hailstone(dataline))
    return hail


def go():
    data_list = list()

    from .DataSample import DAY_24 as SAMPLE

    data_list.append(
        ("Sample", SAMPLE, [(numpy.greater_equal, 7.0), (numpy.less_equal, 27.0)])
    )

    try:
        from .DataFull_ import DAY_24 as DATA

        data_list.append(
            ("Full data", DATA, [(numpy.greater_equal, 2e14), (numpy.less_equal, 4e14)])
        )
    except ImportError:
        pass

    for name, data, limits in data_list:
        print(name)
        hail = load(data.splitlines())

        # PART 1

        # find the collisions
        collision_counts = 0
        for i in range(len(hail)):
            for j in range(i + 1, len(hail)):
                collision, t1, t2 = hail[i].collide_xy(hail[j])

                # collision in past
                if t1 < 0 or t2 < 0:
                    continue
                # no collision in range of interest
                if not all(
                    [operation(collision, limit).all() for operation, limit in limits]
                ):
                    continue
                collision_counts += 1

        print(" ", collision_counts, "collisions in area", [b for a, b in limits])

        # PART 2

        rock_origin, rock_velocity = find_rock(hail)
        print("  Rock origin:", rock_origin, sum(rock_origin))
        print("  Rock velocity:", rock_velocity)


def to_blender(hailstones: Collection["Hailstone"], meshname="Hail"):
    """
    Convert collection of hailstones to a blender mesh with stored velocity.
    """
    import bmesh
    import bpy

    bm = bmesh.new()
    velocity_layer = bm.verts.layers.float_vector.new("velocity")
    for hailstone in hailstones:
        v = bm.verts.new(hailstone.origin)
        v[velocity_layer] = hailstone.velocity
    bm.verts.ensure_lookup_table()

    mesh = bpy.data.meshes.new(meshname)
    bm.to_mesh(mesh)
    bm.free()

    return mesh


if __name__ == "__main__":
    go()
