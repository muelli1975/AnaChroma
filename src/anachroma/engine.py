"""Shared, cancellable Float32 engine for preview and export.

Each half's matrix contribution is clipped before addition, as in the
reference's integer FFmpeg pipeline. Custom presets use this same rule.
"""
from __future__ import annotations

from threading import Event
import numpy as np

from .color_transfer import srgb_to_linear, linear_to_srgb
from .matrices import Method


class Cancelled(Exception):
    """The user cancelled a job before its next safe processing boundary."""


def check_cancel(cancel: Event | None) -> None:
    if cancel is not None and cancel.is_set():
        raise Cancelled("Abgebrochen.")


def make_anaglyph(left: np.ndarray, right: np.ndarray, method: Method,
                  cancel: Event | None = None, block_rows: int = 128) -> np.ndarray:
    method.validate()
    if method.mode == "cielab":
        raise ValueError("CIELab wird über das externe Programm berechnet.")
    if left.shape != right.shape or left.ndim != 3 or left.shape[2] != 3 or not left.size:
        raise ValueError("Zwei gleich große RGB-Halbbilder werden benötigt.")
    if left.dtype != np.uint8 or right.dtype != np.uint8:
        raise TypeError("Die Eingabe muss 8-Bit-RGB sein.")
    if block_rows < 1:
        raise ValueError("Die Streifenhöhe muss positiv sein.")
    check_cancel(cancel)
    ml = np.asarray(method.left, dtype=np.float32).T
    mr = np.asarray(method.right, dtype=np.float32).T
    output = np.empty_like(left)
    for start in range(0, left.shape[0], block_rows):
        check_cancel(cancel)
        end = start + block_rows
        l = left[start:end].astype(np.float32) / np.float32(255.)
        r = right[start:end].astype(np.float32) / np.float32(255.)
        if method.mode == "linear":
            l, r = srgb_to_linear(l), srgb_to_linear(r)
        if method.mode == "iaian7":
            lm = np.array([[.4,.3,.3],[0,0,0],[0,0,0]], dtype=np.float32).T
            rm = np.array([[0,0,0],[.1,.9,0],[.1,0,.9]], dtype=np.float32).T
            a = np.power(np.clip(l @ lm, 0, 1), np.float32(.87))
            b = np.power(np.clip(r @ rm, 0, 1), np.float32(1.176))
            mixed = np.clip(a+b, 0, 1)
            correction = np.array([[1.16,-.08,-.08],[-.02,1.04,-.02],[-.02,-.02,1.04]], dtype=np.float32)
            mixed = np.clip(mixed @ correction.T, 0, 1)
        else:
            mixed = np.clip(l @ ml, 0, 1) + np.clip(r @ mr, 0, 1)
            np.clip(mixed, 0, 1, out=mixed)
            if method.mode == "linear":
                mixed = linear_to_srgb(mixed)
            if method.correct_rgb:
                mixed = np.power(mixed, np.asarray(method.powers, dtype=np.float32))
        output[start:end] = np.clip(np.rint(mixed * 255.), 0, 255).astype(np.uint8)
    return output
