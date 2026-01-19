from adafruit_motorkit import MotorKit
from time import sleep
import threading
import queue


class RobotController:
    def __init__(self):
        try:
            self.kit = MotorKit()
            # pass
        except Exception as e:
            print(f'Warning: MotorKit could not be initialized. Running in simulation mode. Error: {e}')
            
        self.command_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def _move_hardware(self, left: float, right: float):
        # sleep(1)
        # return
        self.kit.motor1.throttle = left
        self.kit.motor2.throttle = right
        sleep(1)
        self.kit.motor1.throttle = 0
        self.kit.motor2.throttle = 0

    def _worker(self):
        """Background worker to process robot commands."""
        while True:
            try:
                command = self.command_queue.get()
                if command == 'stop':
                    break
                
                # Execute command
                if command == 'forward':
                    self._move_hardware(1.0, 1.0)
                elif command == 'backward':
                    self._move_hardware(-1.0, -1.0)
                elif command == 'left':
                    self._move_hardware(1.0, 0.5)
                elif command == 'right':
                    self._move_hardware(0.5, 1.0)
                
                self.command_queue.task_done()
            except Exception as e:
                print(f"Error in robot worker: {e}")

    def move(self, direction):
        """Public API to queue a movement command."""
        if direction in ['forward', 'backward', 'left', 'right']:
            self.command_queue.put(direction)
            return True
        return False

# Initialize the controller
robot_controller = RobotController()
