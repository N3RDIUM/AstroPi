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
    Cooldown: float  # seconds

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
                Count = 1,
                Cooldown = 1
            ),
            state = DeviceState.STOPPED
        )
        count: int = 0

        while self.alive:
            if len(self.command_queue) != 0:
                cmd = self.command_queue.pop(0)
                print(cmd)
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
                    device.start()

                elif isinstance(cmd, StopPreview):
                    if intervalometer.state == DeviceState.STOPPED:
                        print("[INFO] preview already stopped!")
                    elif intervalometer.state == DeviceState.SHOOTING:
                        print("[ERR] cannot stop preview mode while shooting")
                        continue

                    intervalometer.state = DeviceState.STOPPED
                    device.stop()

                elif isinstance(cmd, StartCapture):
                    if intervalometer.state == DeviceState.SHOOTING:
                        print("[INFO] already shooting!")
                    elif intervalometer.state == DeviceState.PREVIEW:
                        print("[ERR] cannot start shooting in preview mode")
                        continue

                    intervalometer.state = DeviceState.SHOOTING
                    device.start()
                    count = 0

                elif isinstance(cmd, StopCapture):
                    if intervalometer.state == DeviceState.STOPPED:
                        print("[INFO] already stopped!")
                    elif intervalometer.state == DeviceState.PREVIEW:
                        print("[ERR] cannot stop shooting in preview mode")
                        continue

                    intervalometer.state = DeviceState.STOPPED
                    device.stop()

                else:
                    print(f"[ERR] unknown command type: {cmd_type}")

            if intervalometer.state == DeviceState.PREVIEW:
                ...

            elif intervalometer.state == DeviceState.SHOOTING:
                if count == intervalometer.controls.Count:
                    device.stop()
                    intervalometer.state = DeviceState.STOPPED
                    print(f"[INFO] {count} images captured successfully")
                    continue

                try:
                    filename = os.path.join(CAPTURE_DIR, f"{uuid4()}.png")
                    _ = device.capture_file(filename)
                except Exception as e:
                    print(f"[ERR] failed to capture: {e}")
                    continue

                # TODO call/provide hooks
                
                print("[INFO] waiting intervalometer")
                time.sleep(intervalometer.controls.Cooldown)
                print("[INFO] wait ended")

                count += 1

    def submit_command(self, command: Command) -> None:
        self.command_queue.append(command)

    def kill(self) -> None:
        self.alive = False
        self.device_thread.join()

