from __future__ import annotations
from typing import Callable, Optional

try:
    import keyboard
    _KEYBOARD_AVAILABLE = True
except ImportError:
    _KEYBOARD_AVAILABLE = False


class PTTController:
    """
    Monitors a configurable hotkey for push-to-talk.
    Calls on_press / on_release callbacks on state change.
    Does not require auto-sync with the simulator.
    """

    def __init__(self, hotkey: str = "space", on_press: Optional[Callable] = None, on_release: Optional[Callable] = None) -> None:
        self.hotkey = hotkey
        self.on_press = on_press or (lambda: None)
        self.on_release = on_release or (lambda: None)
        self._pressed = False
        self._running = False

    def start(self) -> None:
        if not _KEYBOARD_AVAILABLE:
            raise RuntimeError("keyboard library not installed. Run: pip install keyboard")
        self._running = True
        keyboard.on_press_key(self.hotkey, self._handle_press)
        keyboard.on_release_key(self.hotkey, self._handle_release)

    def stop(self) -> None:
        self._running = False
        if _KEYBOARD_AVAILABLE:
            keyboard.unhook_all()

    @property
    def pressed(self) -> bool:
        return self._pressed

    def _handle_press(self, _) -> None:
        if not self._pressed:
            self._pressed = True
            self.on_press()

    def _handle_release(self, _) -> None:
        if self._pressed:
            self._pressed = False
            self.on_release()
