"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import heartbeat_receiver
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def heartbeat_receiver_worker(
    connection: mavutil.mavfile,
    main_queue: queue_proxy_wrapper.QueueProxyWrapper,
    controller: worker_controller.WorkerController,
) -> None:
    """
    Worker process.

    connection: the MAVLink connection used to receive heartbeats
    main_queue: the output queue used to send heartbeat status
    controller: the worker controller used to manage the worker and pause/resume/exit
    """
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (heartbeat_receiver.HeartbeatReceiver)
    result, heartbeat_receiver_object = heartbeat_receiver.HeartbeatReceiver.create(
        connection, local_logger
    )
    if not result:
        local_logger.error("Failed to create heartbeat receiver", True)
        return
    assert heartbeat_receiver_object is not None

    # Main loop: do work.
    while not controller.is_exit_requested():
        try:
            controller.check_pause()
            status = heartbeat_receiver_object.run()
            main_queue.queue.put(status)
        except (OSError, TimeoutError, ValueError) as e:
            local_logger.error(f"Failed to receive heartbeat: {e}", True)
            return


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
