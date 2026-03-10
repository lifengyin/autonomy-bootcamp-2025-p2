"""
Telemetry gathering logic.
"""

from __future__ import annotations

import time

from pymavlink import mavutil

from ..common.modules.logger import logger


class TelemetryData:  # pylint: disable=too-many-instance-attributes
    """
    Python struct to represent Telemtry Data. Contains the most recent attitude and position reading.
    """

    def __init__(
        self,
        time_since_boot: int | None = None,  # ms
        x: float | None = None,  # m
        y: float | None = None,  # m
        z: float | None = None,  # m
        x_velocity: float | None = None,  # m/s
        y_velocity: float | None = None,  # m/s
        z_velocity: float | None = None,  # m/s
        roll: float | None = None,  # rad
        pitch: float | None = None,  # rad
        yaw: float | None = None,  # rad
        roll_speed: float | None = None,  # rad/s
        pitch_speed: float | None = None,  # rad/s
        yaw_speed: float | None = None,  # rad/s
    ) -> None:
        self.time_since_boot = time_since_boot
        self.x = x
        self.y = y
        self.z = z
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        self.z_velocity = z_velocity
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.roll_speed = roll_speed
        self.pitch_speed = pitch_speed
        self.yaw_speed = yaw_speed

    def __str__(self) -> str:
        return f"""{{
            time_since_boot: {self.time_since_boot},
            x: {self.x},
            y: {self.y},
            z: {self.z},
            x_velocity: {self.x_velocity},
            y_velocity: {self.y_velocity},
            z_velocity: {self.z_velocity},
            roll: {self.roll},
            pitch: {self.pitch},
            yaw: {self.yaw},
            roll_speed: {self.roll_speed},
            pitch_speed: {self.pitch_speed},
            yaw_speed: {self.yaw_speed}
        }}"""


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Telemetry:
    """
    Telemetry class to read position and attitude (orientation).
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> tuple[bool, Telemetry | None]:
        """
        Falliable create (instantiation) method to create a Telemetry object.
        """
        try:
            return True, cls(cls.__private_key, connection, local_logger)
        except Exception as e:
            local_logger.error(f"Failed to create telemetry: {e}", True)
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Telemetry.__private_key, "Use create() method"

        self.connection = connection
        self.local_logger = local_logger

    def run(self) -> TelemetryData | None:
        """
        Receive LOCAL_POSITION_NED and ATTITUDE messages from the drone,
        combining them together to form a single TelemetryData object.
        """

        local_pos = None
        attitude = None
        deadline = time.time() + 1.0

        try:
            while time.time() < deadline:
                remaining = deadline - time.time()
                if remaining <= 0:
                    break

                # Read MAVLink message LOCAL_POSITION_NED (32)s
                # Read MAVLink message ATTITUDE (30)
                message = self.connection.recv_match(
                    type=["LOCAL_POSITION_NED", "ATTITUDE"], blocking=True, timeout=remaining
                )
                if message is None:
                    break

                message_type = message.get_type()
                if message_type == "LOCAL_POSITION_NED":
                    local_pos = message
                elif message_type == "ATTITUDE":
                    attitude = message

                # Small optimization to exit if we have both messages
                if local_pos is not None and attitude is not None:
                    break

            if local_pos is None or attitude is None:
                self.local_logger.error("Failed to receive local position or attitude", True)
                return None

            # Return the most recent of both, and use the most recent message's timestamp
            most_recent_time = max(local_pos.time_boot_ms, attitude.time_boot_ms)

            return TelemetryData(
                time_since_boot=most_recent_time,
                x=local_pos.x,
                y=local_pos.y,
                z=local_pos.z,
                x_velocity=local_pos.vx,
                y_velocity=local_pos.vy,
                z_velocity=local_pos.vz,
                roll=attitude.roll,
                pitch=attitude.pitch,
                yaw=attitude.yaw,
                roll_speed=attitude.rollspeed,
                pitch_speed=attitude.pitchspeed,
                yaw_speed=attitude.yawspeed,
            )

        except Exception as e:
            self.local_logger.error(f"Failed to receive telemetry: {e}", True)
            return None


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
