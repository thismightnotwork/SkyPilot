from __future__ import annotations
from typing import Callable, Optional


class PTTController:
    """Keyboard push-to-talk controller.

    Uses the `keyboard` package for global hotkey detection.
    Falls back gracefully if the package is unavailable or permissions are denied.
    """

    def __init__(
        self,
        hotkey: str = 'space',
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None,
    ):
        self.hotkey = hotkey
        self.on_press = on_press
        self.on_release = on_release
        self.pressed = False
        self._kb = None
        self.active = False

    def start(self) -> bool:
        try:
            import keyboard
            self._kb = keyboard
            keyboard.on_press_key(self.hotkey, lambda _: self._set(True), suppress=False)
            keyboard.on_release_key(self.hotkey, lambda _: self._set(False), suppress=False)
            self.active = True
            return True
        except Exception:
            self.active = False
            return False

    def stop(self):
        if self._kb:
            try:
                self._kb.unhook_all()
            except Exception:
                pass
        self.active = False
        self.pressed = False

    def _set(self, value: bool):
        if self.pressed == value:
            return
        self.pressed = value
        if value and self.on_press:
            self.on_press()
        elif not value and self.on_release:
            self.on_release()
