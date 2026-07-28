"""Exact numerical behavior shared by compiler and simulator tests."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

INT8_MIN = -128
INT8_MAX = 127
INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1


def _require_integer(value: object, name: str) -> int:
    """Return one integer without accepting lossy scalar coercions."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, np.integer)
    ):
        raise ValueError(f"{name} must be an integer")
    return int(value)


def _integer_array(value: object, name: str) -> np.ndarray:
    """Create an integer array without coercing floats, strings, or booleans."""
    array = np.asarray(value)
    if array.dtype.kind not in {"i", "u"}:
        raise ValueError(f"{name} must contain integers")
    return array


def clamp(value: int, minimum: int, maximum: int) -> int:
    """Clamp an integer to an inclusive range."""
    value = _require_integer(value, "value")
    minimum = _require_integer(minimum, "minimum")
    maximum = _require_integer(maximum, "maximum")
    if minimum > maximum:
        raise ValueError("minimum must not exceed maximum")
    return min(max(value, minimum), maximum)


def wrap_i32(value: int) -> int:
    """Wrap an integer to a two's-complement signed 32-bit value."""
    value = _require_integer(value, "value")
    return ((value + (1 << 31)) % (1 << 32)) - (1 << 31)


def round_divide_by_power_of_two(value: int, shift: int) -> int:
    """Divide by 2**shift using round-to-nearest, ties-to-even."""
    value = _require_integer(value, "value")
    shift = _require_integer(shift, "shift")
    if not 0 <= shift <= 62:
        raise ValueError("shift must be in [0, 62]")
    if shift == 0:
        return value

    magnitude = abs(value)
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
    """Apply the ABI 1.0 fixed-point scale and signed INT8 saturation."""
    value = _require_integer(value, "value")
    multiplier = _require_integer(multiplier, "multiplier")
    shift = _require_integer(shift, "shift")
    zero_point = _require_integer(zero_point, "zero_point")
    minimum = _require_integer(minimum, "minimum")
    maximum = _require_integer(maximum, "maximum")
    if not INT32_MIN <= value <= INT32_MAX:
        raise ValueError("value must fit signed INT32")
    if not 1 <= multiplier <= INT32_MAX:
        raise ValueError("multiplier must be in [1, INT32_MAX]")
    if zero_point != 0:
        raise ValueError("ABI 1.0 zero point must be zero")
    if not INT8_MIN <= minimum <= maximum <= INT8_MAX:
        raise ValueError("requantization clamp must fit signed INT8")
    product = value * multiplier
    rounded = round_divide_by_power_of_two(product, shift)
    return clamp(rounded, minimum, maximum)


def quantize_s8(real_value: float, scale: float, zero_point: int = 0) -> int:
    """Quantize one finite float using ties-to-even and signed saturation."""
    if not math.isfinite(real_value):
        raise ValueError("real value must be finite")
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("scale must be positive and finite")
    zero_point = _require_integer(zero_point, "zero_point")
    if not INT8_MIN <= zero_point <= INT8_MAX:
        raise ValueError("zero point must fit signed INT8")
    scaled = real_value / scale
    if not math.isfinite(scaled):
        return INT8_MAX if scaled > 0.0 else INT8_MIN

    upper = INT8_MAX - zero_point
    lower = INT8_MIN - zero_point
    if scaled >= upper + 0.5:
        return INT8_MAX
    if scaled <= lower - 0.5:
        return INT8_MIN

    rounded = int(round(scaled))
    return clamp(rounded + zero_point, INT8_MIN, INT8_MAX)


def dequantize_s8(value: int, scale: float, zero_point: int = 0) -> float:
    """Dequantize one signed INT8 value."""
    value = _require_integer(value, "value")
    zero_point = _require_integer(zero_point, "zero_point")
    if not INT8_MIN <= value <= INT8_MAX:
        raise ValueError("value must fit signed INT8")
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("scale must be positive and finite")
    if not INT8_MIN <= zero_point <= INT8_MAX:
        raise ValueError("zero point must fit signed INT8")
    result = scale * (value - zero_point)
    if not math.isfinite(result):
        raise ValueError("dequantized result must be finite")
    return result


def gemm_s8s8_s32(
    a: Sequence[Sequence[int]] | np.ndarray,
    b: Sequence[Sequence[int]] | np.ndarray,
    bias: Sequence[int] | np.ndarray | None = None,
) -> np.ndarray:
    """Reference GEMM with signed INT8 inputs and wrapping INT32 accumulation."""
    a_array = _integer_array(a, "A")
    b_array = _integer_array(b, "B")
    if a_array.ndim != 2 or b_array.ndim != 2:
        raise ValueError("GEMM inputs must be rank-2")
    if a_array.shape[1] != b_array.shape[0]:
        raise ValueError("GEMM K dimensions do not match")
    if np.any((a_array < INT8_MIN) | (a_array > INT8_MAX)):
        raise ValueError("A contains values outside signed INT8")
    if np.any((b_array < INT8_MIN) | (b_array > INT8_MAX)):
        raise ValueError("B contains values outside signed INT8")

    a_array = a_array.astype(np.int64, copy=False)
    b_array = b_array.astype(np.int64, copy=False)

    m, k = a_array.shape
    _, n = b_array.shape
    if m == 0 or n == 0 or k == 0:
        raise ValueError("GEMM dimensions M, N, and K must be nonzero")
    if bias is None:
        bias_array = np.zeros(n, dtype=np.int64)
    else:
        bias_array = _integer_array(bias, "bias")
        if bias_array.shape != (n,):
            raise ValueError("bias must have shape [N]")
        if np.any((bias_array < INT32_MIN) | (bias_array > INT32_MAX)):
            raise ValueError("bias contains values outside signed INT32")
        bias_array = bias_array.astype(np.int64, copy=False)

    output = np.empty((m, n), dtype=np.int32)
    for row in range(m):
        for column in range(n):
            accumulator = wrap_i32(int(bias_array[column]))
            for inner in range(k):
                product = int(a_array[row, inner]) * int(b_array[inner, column])
                accumulator = wrap_i32(accumulator + product)
            output[row, column] = accumulator
    return output
