"""Immutable definitions from AnaglyphBatch 8ef0a5d (7 October 2026).

Rows are output R/G/B; columns are input R/G/B. The values are not
normalized, rounded or adapted to a different anaglyph color combination.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import math
import re
import uuid
import numpy as np

# Numeric guards only: leave room for matrix sums in Float32. These are not
# recommended photographic settings or slider limits.
MAX_SAFE_VALUE = float(np.finfo(np.float32).max) / 12
MIN_POWER = float(np.finfo(np.float32).smallest_subnormal)

Matrix = tuple[tuple[float, float, float], ...]
ZERO: Matrix = ((0., 0., 0.), (0., 0., 0.), (0., 0., 0.))
LCD_L: Matrix = ((.4561, .500484, .176381), (-.0400822, -.0378246, -.0157589),
                 (-.0152161, -.0205971, -.00546856))
LCD_R: Matrix = ((-.0434706, -.0879388, -.00155529), (.378476, .73364, -.0184503),
                 (-.0721527, -.112961, 1.2264))


@dataclass(frozen=True)
class Method:
    id: str
    name: str
    suffix: str
    left: Matrix = ZERO
    right: Matrix = ZERO
    mode: str = "srgb"
    powers: tuple[float, float, float] = (1., 1., 1.)
    correct_rgb: bool = False
    builtin: bool = True

    @property
    def editable(self) -> bool:
        return self.mode in {"srgb", "linear"}

    def validate(self) -> "Method":
        if not isinstance(self.name, str) or not self.name.strip() or len(self.name) > 120:
            raise ValueError("Bitte einen Namen mit höchstens 120 Zeichen eingeben.")
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("Das Verfahren benötigt eine eindeutige Kennung.")
        if not isinstance(self.suffix, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", self.suffix):
            raise ValueError("Suffix: Kleinbuchstaben, Ziffern und Unterstriche; mit Buchstabe beginnen.")
        if self.mode not in {"srgb", "linear", "rendepth", "iaian7", "cielab"}:
            raise ValueError("Unbekannte Rechenfolge.")
        if not self.builtin and self.mode not in {"srgb", "linear"}:
            raise ValueError("Eigene Verfahren verwenden sRGB oder lineares Licht.")
        for matrix in (self.left, self.right):
            if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
                raise ValueError("Es werden zwei 3×3-Matrizen benötigt.")
            for row in matrix:
                # Bound only by safe Float32 arithmetic, not a photographic UI limit.
                if any(isinstance(x, bool) or not math.isfinite(x) or abs(x) > MAX_SAFE_VALUE for x in row):
                    raise ValueError("Matrixwerte müssen endlich und in Float32 berechenbar sein.")
        if len(self.powers) != 3 or any(isinstance(x, bool) or not math.isfinite(x) or x < MIN_POWER or x > MAX_SAFE_VALUE for x in self.powers):
            raise ValueError("Kanalpotenzen müssen positiv und endlich sein.")
        if not isinstance(self.correct_rgb, bool):
            raise ValueError("Ungültige Einstellung zur Kanalkorrektur.")
        return self

    def as_custom(self, *, existing: bool = False) -> "Method":
        if not self.editable:
            raise ValueError("Dieses Spezialverfahren lässt sich nicht vollständig im Matrixeditor abbilden.")
        return replace(self, id=self.id if existing else f"custom:{uuid.uuid4().hex}",
                       name=self.name if existing else f"{self.name} – eigene Variante",
                       suffix=self.suffix if existing else f"eigen_{self.suffix}",
                       mode="linear" if self.mode == "linear" else "srgb", builtin=False)


def _m(number, name, suffix, left=ZERO, right=ZERO, mode="srgb", powers=(1., 1., 1.)):
    return Method(f"builtin:{number}", name, suffix, left, right, mode, powers,
                  correct_rgb=powers != (1., 1., 1.)).validate()


BUILTINS = (
    _m(1, "Dubois LCD (Sanders/McAllister) + rot", "dubois_lcd", LCD_L, LCD_R, "linear", (.75, 1., 1.)),
    _m(2, "Dubois", "dubois", ((.437,.449,.164),(-.062,-.062,-.024),(-.048,-.05,-.017)),
       ((-.011,-.032,-.007),(.377,.761,-.009),(-.026,-.093,1.234)), "linear"),
    _m(3, "Optimized (Peter Wimmer)", "wimmer", ((0.,.7,.3),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(0.,1.,0.),(0.,0.,1.)), powers=(.6666667,1.,1.)),
    _m(4, "Cosima AnaglyphType=3 (Gerhard P. Herbig)", "cosima3", ((.299,.587,.114),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(.299,.701,0.),(.299,0.,.701)), "linear", (.75,1.,1.)),
    _m(5, "Cosima AnaglyphType=4 (Gerhard P. Herbig)", "cosima4", ((.6495,.2935,.057),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(.1495,.8505,.057),(.1495,.057,.8505)), "linear", (.75,1.,1.)),
    _m(6, "Compromise (Jure Ahtik)", "compromise", ((.439,.447,.148),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(.095,.934,-.005),(-.018,-.028,1.057))),
    _m(7, "iaian7 Anachrome (John Einselen)", "iaian7", mode="iaian7"),
    _m(8, "Rendepth (Andres Hernandez)", "rendepth", LCD_L, LCD_R, "rendepth", (.625,1.25,1.)),
    _m(9, "Rendepth 2 (Andres Hernandez)", "rendepth2", ((.439,.447,.148),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(.095,.934,-.028),(-.018,-.005,1.057)), "rendepth", (.625,1.25,1.)),
    _m(10, "Color", "color", ((1.,0.,0.),(0.,0.,0.),(0.,0.,0.)), ((0.,0.,0.),(0.,1.,0.),(0.,0.,1.))),
    _m(11, "Half-Color", "halfcolor", ((.299,.587,.114),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(0.,1.,0.),(0.,0.,1.))),
    _m(12, "Grey", "grey", ((.299,.587,.114),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(.299,.587,.114),(.299,.587,.114))),
    _m(13, "Oldschool ;)", "oldschool", ((.299,.587,.114),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(.299,.587,.114),(0.,0.,0.))),
    _m(14, "Frans van den Poel", "vdp", ((.5,.5,0.),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(.4,.6,0.),(.2,0.,.8))),
    _m(15, "John Wattie", "wattie", ((.8,.2,.2),(0.,0.,0.),(0.,0.,0.)),
       ((0.,0.,0.),(.2,.8,0.),(.1,0.,.9))),
    _m(16, "CIELab Least Squares (David McAllister)", "cielab", mode="cielab"),
    _m(17, "Dubois grün/magenta (GM)", "dubois_gm", ((-.062,-.158,-.039),(.284,.668,.143),(-.015,-.027,.021)),
       ((.529,.705,.024),(-.016,-.015,-.065),(.009,.075,.937)), "linear"),
    _m(18, "Dubois amber/blau (YB)", "dubois_yb", ((1.062,-.205,.299),(-.026,.908,.068),(-.038,-.173,.022)),
       ((-.016,-.123,-.017),(.006,.062,-.017),(.094,.185,.911)), "linear"),
)
