"""Exact numerical behavior shared by compiler and simulator tests."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

INT8_MIN = -128
INT8_MAX = 127
INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1


def clamp(value: int, minimum: int, maximum: int) -> int:
    """Clamp an integer to an inclusive range."""
    if minimum > maximum:
        raise ValueError("minimum must not exceed maximum")
    return min(max(value, minimum), maximum)


def wrap_i32(value: int) -> int:
    """Wrap an integer to a two's-complement signed 32-bit value."""
    return ((int(value) + (1 << 31)) % (1 << 32)) - (1 << 31)


def round_divide_by_power_of_two(value: int, shift: int) -> int:
    """Divide by 2**shift using round-to-nearest, ties-to-even."""
    if not 0 <= shift <= 62:
        raise ValueError("shift must be in [0, 62]")
    if shift == 0:
        return int(value)

    magnitude = abs(int(value))
    divisor = 1 << shift
    quotient, remainder = divmod(magnitude, divisor)
    twice_remainder = remainder << 1
    if twice_remainder > divisor or (
        twice_remainder == divisor and quotient & 1
    ):
        quotient += 1
    return -quotient if value < 0 else quotient


def requantize_s32_to_s8(
    value: int,
    multiplier: int,
    shift: int,
    zero_point: int = 0,
    minimum: int = INT8_MIN,
    maximum: int = INT8_MAX,
) -> int:
    """Apply a fixed-point scale and saturate to an INT8-compatible range."""
    if not INT8_MIN <= minimum <= maximum <= INT8_MAX:
        raise ValueError("requantization clamp must fit signed INT8")
    product = int(value) * int(multiplier)
    rounded = round_divide_by_power_of_two(product, shift)
    return clamp(rounded + int(zero_point), minimum, maximum)


def quantize_s8(real_value: float, scale: float, zero_point: int = 0) -> int:
    """Quantize one finite float using ties-to-even and signed saturation."""
    if not math.isfinite(real_value):
        raise ValueError("real value must be finite")
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("scale must be positive and finite")
    if not INT8_MIN <= zero_point <= INT8_MAX:
        raise ValueError("zero point must fit signed INT8")
    rounded = int(round(real_value / scale))
    return clamp(rounded + zero_point, INT8_MIN, INT8_MAX)


def dequantize_s8(value: int, scale: float, zero_point: int = 0) -> float:
    """Dequantize one signed INT8 value."""
    if not INT8_MIN <= value <= INT8_MAX:
        raise ValueError("value must fit signed INT8")
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("scale must be positive and finite")
    if not INT8_MIN <= zero_point <= INT8_MAX:
        raise ValueError("zero point must fit signed INT8")
    return scale * (int(value) - int(zero_point))


def gemm_s8s8_s32(
    a: Sequence[Sequence[int]] | np.ndarray,
    b: Sequence[Sequence[int]] | np.ndarray,
    bias: Sequence[int] | np.ndarray | None = None,
) -> np.ndarray:
    """Reference GEMM with signed INT8 inputs and wrapping INT32 accumulation."""
    a_array = np.asarray(a, dtype=np.int64)
    b_array = np.asarray(b, dtype=np.int64)
    if a_array.ndim != 2 or b_array.ndim != 2:
        raise ValueError("GEMM inputs must be rank-2")
    if a_array.shape[1] != b_array.shape[0]:
        raise ValueError("GEMM K dimensions do not match")
    if np.any((a_array < INT8_MIN) | (a_array > INT8_MAX)):
        raise ValueError("A contains values outside signed INT8")
    if np.any((b_array < INT8_MIN) | (b_array > INT8_MAX)):
        raise ValueError("B contains values outside signed INT8")

    m, k = a_array.shape
    _, n = b_array.shape
    if bias is None:
        bias_array = np.zeros(n, dtype=np.int64)
    else:
        bias_array = np.asarray(bias, dtype=np.int64)
        if bias_array.shape != (n,):
            raise ValueError("bias must have shape [N]")
        if np.any((bias_array < INT32_MIN) | (bias_array > INT32_MAX)):
            raise ValueError("bias contains values outside signed INT32")

    output = np.empty((m, n), dtype=np.int32)
    for row in range(m):
        for column in range(n):
            accumulator = wrap_i32(int(bias_array[column]))
            for inner in range(k):
                product = int(a_array[row, inner]) * int(b_array[inner, column])
                accumulator = wrap_i32(accumulator + product)
            output[row, column] = accumulator
    return output
