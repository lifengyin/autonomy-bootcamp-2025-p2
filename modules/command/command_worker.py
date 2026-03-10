"""
Command worker to make decisions based on Telemetry Data.
"""

import os
import pathlib
import queue

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import command
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def command_worker(
    connection: mavutil.mavfile,
    target: command.Position,
    telemetry_queue: queue_proxy_wrapper.QueueProxyWrapper,
    main_queue: queue_proxy_wrapper.QueueProxyWrapper,
    controller: worker_controller.WorkerController,
) -> None:
    """
    Worker process.

    connection: the MAVLink connection used to send commands
    target: the target position to move to
    telemetry_queue: the input queue used to receive telemetry data
    main_queue: the output queue used to send command status strings
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

    # Instantiate class object (command.Command)
    result, command_object = command.Command.create(connection, target, local_logger)
    if not result:
        local_logger.error("Failed to create command object", True)
        return
    assert command_object is not None

    # Main loop: do work.
    while not controller.is_exit_requested():
        try:
            controller.check_pause()
            command_data = telemetry_queue.queue.get(timeout=0.1)
            result = command_object.run(command_data)
            if result != "NO_COMMAND":
                main_queue.queue.put(result)
        except queue.Empty:
            continue
        except Exception as e:
            local_logger.error(f"Failed to run command: {e}", True)
            return


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
