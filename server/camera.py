import os
from uuid import uuid4
from dataclasses import dataclass
from threading import Thread
import picamera2
from picamera2.platform import Enum
import time

CAPTURE_DIR = "./capture"
if not os.path.isdir(CAPTURE_DIR):
    os.mkdir(CAPTURE_DIR)

@dataclass
class CameraControls:
    AnalogueGain: float
    ExposureTime: int  # microseconds

@dataclass
class IntervalometerControls:
    Count: int
    Cooldown: int  # microseconds

@dataclass
class Command: ...

@dataclass
class UpdateControls:
    controls: CameraControls

@dataclass
class UpdateIntervalomater:
    controls: IntervalometerControls

@dataclass
class StartPreview: ...

@dataclass
class StopPreview: ...

@dataclass
class StartCapture: ...

@dataclass
class StopCapture: ...

class DeviceState(Enum):
    STOPPED = 0
    PREVIEW = 1
    SHOOTING = 2

@dataclass
class Intervalometer:
    state: DeviceState
    controls: IntervalometerControls


class Camera:
    """Wraps Picamera2 for use in a flask server"""

    command_queue: list[Command]
    device_thread: Thread
    alive: bool

    def __init__(self) -> None:
        self.command_queue = []  # FIFO
        self.alive = True

        self.device_thread = Thread(
            target = self._device_thread,
            daemon = True
        )
        self.device_thread.start()

    def _device_thread(self):
        device = picamera2.Picamera2()
        intervalometer = Intervalometer(
            controls = IntervalometerControls(
                Count = 0,
                Cooldown = 0
            ),
            state = DeviceState.STOPPED
        )

        while self.alive:
            print("tick")

            if intervalometer.state == DeviceState.PREVIEW:
                ...
            elif intervalometer.state == DeviceState.SHOOTING:
                try:
                    device.start()
                    filename = os.path.join(CAPTURE_DIR, f"{uuid4()}.dng")
                    _ = device.capture_file(filename)
                    device.stop()
                except Exception as e:
                    print(f"[ERR] failed to capture: {e}")

                # TODO call/provide hooks
                
                time.sleep(intervalometer.controls.Cooldown)
                intervalometer.controls.Count -= 1

                if intervalometer.controls.Count == 0:
                    intervalometer.state = DeviceState.STOPPED

            if len(self.command_queue) != 0:
                cmd = self.command_queue.pop(0)
                cmd_type = type(cmd)

                if cmd_type == Command:
                    print("[WARN] device received empty command")
                    continue

                elif isinstance(cmd, UpdateControls):
                    if intervalometer.state != DeviceState.STOPPED:
                        print("[ERR] device not stopped, cannot update controls")
                        continue

                    try:
                        controls = cmd.controls
                        device.set_controls({
                            "AnalogueGain": controls.AnalogueGain,
                            "ExposureTime": controls.ExposureTime
                        })
                        print("[INFO] set device controls successfully")
                    except Exception as e:
                        print(f"[ERR] could not set device controls: {e}")
                        continue

                elif isinstance(cmd, UpdateIntervalomater):
                    if intervalometer.state != DeviceState.STOPPED:
                        print("[ERR] device not stopped, cannot update intervalometer")
                        continue

                    intervalometer.controls = cmd.controls

                elif isinstance(cmd, StartPreview):
                    if intervalometer.state == DeviceState.PREVIEW:
                        print("[INFO] preview already running!")
                    elif intervalometer.state == DeviceState.SHOOTING:
                        print("[ERR] cannot start preview mode while shooting")
                        continue

                    intervalometer.state = DeviceState.PREVIEW

                elif isinstance(cmd, StopPreview):
                    if intervalometer.state == DeviceState.STOPPED:
                        print("[INFO] preview already stopped!")
                    elif intervalometer.state == DeviceState.SHOOTING:
                        print("[ERR] cannot stop preview mode while shooting")
                        continue

                    intervalometer.state = DeviceState.STOPPED

                elif isinstance(cmd, StartCapture):
                    if intervalometer.state == DeviceState.SHOOTING:
                        print("[INFO] already shooting!")
                    elif intervalometer.state == DeviceState.PREVIEW:
                        print("[ERR] cannot start shooting in preview mode")
                        continue

                    intervalometer.state = DeviceState.SHOOTING

                elif isinstance(cmd, StopCapture):
                    if intervalometer.state == DeviceState.STOPPED:
                        print("[INFO] already stopped!")
                    elif intervalometer.state == DeviceState.PREVIEW:
                        print("[ERR] cannot stop shooting in preview mode")
                        continue

                    intervalometer.state = DeviceState.STOPPED

                else:
                    print(f"[ERR] unknown command type: {cmd_type}")

    def submit_command(self, command: Command) -> None:
        self.command_queue.append(command)

    def kill(self) -> None:
        self.alive = False
        self.device_thread.join()

