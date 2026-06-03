"""
ptt.py — Push-to-talk controller.
"""
from __future__ import annotations
import threading
from typing import Callable, Dict, Optional


class PTTController:
    def __init__(self):
        self._bindings: Dict[str, dict] = {}
        self.on_change: Optional[Callable[[str, bool], None]] = None
        self._kb   = None
        self._joy  = None
        self._joy_thread: Optional[threading.Thread] = None
        self._running = False

    def bind(self, channel: str, hotkey: Optional[str] = None, joystick_btn: Optional[int] = None):
        self._bindings[channel] = {
            'hotkey': hotkey,
            'joystick_btn': joystick_btn,
            'pressed': False,
        }

    def start(self) -> bool:
        self._running = True
        ok = False
        try:
            import keyboard
            self._kb = keyboard
            for ch, b in self._bindings.items():
                if b['hotkey']:
                    def _make_handlers(channel, binding):
                        def on_press(e):
                            if not binding['pressed']:
                                binding['pressed'] = True
                                if self.on_change:
                                    self.on_change(channel, True)
                        def on_release(e):
                            if binding['pressed']:
                                binding['pressed'] = False
                                if self.on_change:
                                    self.on_change(channel, False)
                        return on_press, on_release
                    p, r = _make_handlers(ch, b)
                    keyboard.on_press_key(b['hotkey'],   p, suppress=False)
                    keyboard.on_release_key(b['hotkey'], r, suppress=False)
            ok = True
        except Exception:
            pass

        joy_channels = {ch: b for ch, b in self._bindings.items() if b['joystick_btn'] is not None}
        if joy_channels:
            try:
                import pygame
                pygame.init()
                pygame.joystick.init()
                if pygame.joystick.get_count() > 0:
                    self._joy = pygame.joystick.Joystick(0)
                    self._joy.init()
                    self._joy_thread = threading.Thread(
                        target=self._joy_loop,
                        args=(joy_channels,),
                        daemon=True,
                    )
                    self._joy_thread.start()
            except Exception:
                pass

        return ok

    def stop(self):
        self._running = False
        if self._kb:
            try:
                self._kb.unhook_all()
            except Exception:
                pass
        for b in self._bindings.values():
            b['pressed'] = False

    def is_pressed(self, channel: str) -> bool:
        return self._bindings.get(channel, {}).get('pressed', False)

    def _joy_loop(self, joy_channels: dict):
        import pygame
        clock = pygame.time.Clock()
        while self._running:
            pygame.event.pump()
            for ch, b in joy_channels.items():
                btn = b['joystick_btn']
                try:
                    pressed = bool(self._joy.get_button(btn))
                except Exception:
                    pressed = False
                if pressed != b['pressed']:
                    b['pressed'] = pressed
                    if self.on_change:
                        self.on_change(ch, pressed)
            clock.tick(30)
