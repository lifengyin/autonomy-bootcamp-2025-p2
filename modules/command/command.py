"""
Decision-making logic.
"""

from __future__ import annotations

import math

from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> tuple[bool, Command | None]:
        """
        Falliable create (instantiation) method to create a Command object.
        """
        try:
            command_object = cls(cls.__private_key, connection, target, local_logger)
            return True, command_object
        except Exception as e:
            local_logger.error(f"Failed to create command: {e}", True)
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        self.connection = connection
        self.target = target
        self.local_logger = local_logger

        self.velocity_sample_count = 0
        self.velocity_sum_x = 0.0
        self.velocity_sum_y = 0.0
        self.velocity_sum_z = 0.0

        self.height_tolerance = 0.5
        self.z_speed = 1.0
        self.angle_tolerance_deg = 5.0
        self.turning_speed_deg_s = 5.0

    def run(
        self,
        telemetry_data: telemetry.TelemetryData,
    ) -> str:
        """
        Make a decision based on received telemetry data.
        """

        try:
            # Log average velocity of all received telemetry so far.
            if (
                telemetry_data.x_velocity is not None
                and telemetry_data.y_velocity is not None
                and telemetry_data.z_velocity is not None
            ):
                self.velocity_sample_count += 1
                count = self.velocity_sample_count

                self.velocity_sum_x += telemetry_data.x_velocity
                self.velocity_sum_y += telemetry_data.y_velocity
                self.velocity_sum_z += telemetry_data.z_velocity

                avg_velocity_x = self.velocity_sum_x / count
                avg_velocity_y = self.velocity_sum_y / count
                avg_velocity_z = self.velocity_sum_z / count

                self.local_logger.info(
                    (
                        "Average velocity: "
                        f"x: {avg_velocity_x:.3f} m/s"
                        f"y: {avg_velocity_y:.3f} m/s"
                        f"z: {avg_velocity_z:.3f} m/s"
                    ),
                    True,
                )

            # Altitude command: move up/down to target z.
            if telemetry_data.z is not None:
                dz = self.target.z - telemetry_data.z

                # If too far, adjust altitude to target z
                if abs(dz) > self.height_tolerance:
                    self.connection.mav.command_long_send(
                        1,
                        0,
                        mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT,
                        0,
                        float(self.z_speed),
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        float(self.target.z),
                    )
                    return f"CHANGE ALTITUDE: {dz:.3f}"

            # Yaw command: rotate to face target.
            if (
                telemetry_data.x is not None
                and telemetry_data.y is not None
                and telemetry_data.yaw is not None
            ):
                # Use arctan to get desired yaw angle in rad
                yaw_rad = math.atan2(
                    self.target.y - telemetry_data.y, self.target.x - telemetry_data.x
                )
                # Find change in yaw in degrees.
                yaw_delta_deg = math.degrees(yaw_rad - telemetry_data.yaw)
                # Convert to angle from -180 to 180 deg.
                signed_yaw_deg = ((yaw_delta_deg + 180.0) % 360.0) - 180.0

                if abs(signed_yaw_deg) > self.angle_tolerance_deg:
                    self.connection.mav.command_long_send(
                        1,
                        0,
                        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
                        0,
                        float(signed_yaw_deg),
                        float(self.turning_speed_deg_s),
                        0.0,
                        1.0,
                        0.0,
                        0.0,
                        0.0,
                    )
                    return f"CHANGE YAW: {signed_yaw_deg:.3f}"
        except Exception as e:
            self.local_logger.error(f"Failed to run command: {e}", True)
            return "NO_COMMAND"

        return "NO_COMMAND"


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
