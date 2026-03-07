"""
Heartbeat receiving logic.
"""

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
        args,  # Put your own arguments here
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        self.connection = connection
        self.missed_heartbeats = 0
        self.max_missed_heartbeats = 5
        self.is_connected = False

    def run(
        self,
        args,  # Put your own arguments here
    ):
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        pass


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
