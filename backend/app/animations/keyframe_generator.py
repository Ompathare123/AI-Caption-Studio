import math


class KeyframeGenerator:

    @staticmethod
    def linear(t: float) -> float:
        return t

    @staticmethod
    def ease_in(t: float) -> float:
        return t * t

    @staticmethod
    def ease_out(t: float) -> float:
        return 1.0 - (1.0 - t) * (1.0 - t)

    @staticmethod
    def ease_in_out(t: float) -> float:
        if t < 0.5:
            return 2.0 * t * t
        else:
            return 1.0 - ((-2.0 * t + 2.0) ** 2) / 2.0

    @staticmethod
    def bounce(t: float) -> float:
        n1 = 7.5625
        d1 = 2.75

        if t < 1.0 / d1:
            return n1 * t * t
        elif t < 2.0 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375

    @staticmethod
    def elastic(t: float) -> float:
        c4 = (2.0 * math.pi) / 3.0
        if t == 0.0:
            return 0.0
        elif t == 1.0:
            return 1.0
        else:
            # Shifted standard elastic formula returning 0 to 1 range
            return (
                math.pow(2.0, -10.0 * t) * math.sin((t * 10.0 - 0.75) * c4)
                + 1.0
            )

    @staticmethod
    def interpolate(easing: str, t: float) -> float:
        """
        Clamps progress t to [0.0, 1.0] and returns the interpolated progress.
        """
        t = max(0.0, min(1.0, t))
        easings = {
            "linear": KeyframeGenerator.linear,
            "ease_in": KeyframeGenerator.ease_in,
            "ease_out": KeyframeGenerator.ease_out,
            "ease_in_out": KeyframeGenerator.ease_in_out,
            "bounce": KeyframeGenerator.bounce,
            "elastic": KeyframeGenerator.elastic,
        }
        func = easings.get(easing.lower().strip(), KeyframeGenerator.linear)
        return func(t)
