"""
Heartbeat receiving logic.
"""

from __future__ import annotations

from pymavlink import mavutil

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> tuple[bool, HeartbeatReceiver | None]:
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """

        try:
            heartbeat_reciever_object = cls(cls.__private_key, connection, local_logger)
            return True, heartbeat_reciever_object
        except Exception as e:
            local_logger.error(f"Failed to create heartbeat receiver: {e}", True)
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        self.connection = connection
        self.local_logger = local_logger
        self.missed_heartbeats = 0
        self.max_missed_heartbeats = 5
        self.is_connected = False

    def run(self) -> str:
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """

        try:
            message = self.connection.recv_match(type="HEARTBEAT", blocking=True, timeout=1)

            if message is not None:
                self.missed_heartbeats = 0
                self.is_connected = True
            else:
                self.missed_heartbeats += 1
                self.local_logger.warning(
                    f"Missed heartbeat {self.missed_heartbeats} (out of a max of {self.max_missed_heartbeats})",
                    True,
                )

                if self.missed_heartbeats >= self.max_missed_heartbeats:
                    self.is_connected = False

            return "Connected" if self.is_connected else "Disconnected"

        except Exception as e:
            self.local_logger.error(f"Failed to receive heartbeat: {e}", True)
            return "Connected" if self.is_connected else "Disconnected"


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
