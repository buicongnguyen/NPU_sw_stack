from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pytest

from npu_lab.numerics import (
    dequantize_s8,
    gemm_s8s8_s32,
    quantize_s8,
    requantize_s32_to_s8,
    round_divide_by_power_of_two,
    wrap_i32,
)

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "numerics"


class XorShift32:
    """Versioned fixture PRNG shared with the C++ contract test."""

    def __init__(self, seed: int) -> None:
        if not 0 < seed <= 0xFFFF_FFFF:
            raise ValueError("xorshift32 seed must be a nonzero uint32")
        self.state = seed

    def next_u32(self) -> int:
        value = self.state
        value ^= (value << 13) & 0xFFFF_FFFF
        value ^= value >> 17
        value ^= (value << 5) & 0xFFFF_FFFF
        self.state = value & 0xFFFF_FFFF
        return self.state

    def integer(self, minimum: int, maximum: int) -> int:
        return minimum + self.next_u32() % (maximum - minimum + 1)


def load_gemm_corpus_config() -> tuple[int, int, int, int, int]:
    with (FIXTURE_ROOT / "gemm-corpus.csv").open(
        newline="", encoding="utf-8"
    ) as file:
        rows = csv.reader(line for line in file if not line.startswith("#"))
        fields = tuple(map(int, next(rows)))
        if len(fields) != 5:
            raise ValueError("GEMM corpus configuration must have five fields")
        return fields[0], fields[1], fields[2], fields[3], fields[4]


def test_round_divide_ties_to_even() -> None:
    cases = {
        (1, 1): 0,
        (3, 1): 2,
        (5, 1): 2,
        (7, 1): 4,
        (-1, 1): 0,
        (-3, 1): -2,
        (-5, 1): -2,
        (-7, 1): -4,
    }
    for arguments, expected in cases.items():
        assert round_divide_by_power_of_two(*arguments) == expected


def test_requantize_shared_fixture() -> None:
    with (FIXTURE_ROOT / "requantize.csv").open(newline="", encoding="utf-8") as file:
        rows = csv.reader(line for line in file if not line.startswith("#"))
        for row in rows:
            value, multiplier, shift, zero_point, minimum, maximum, expected = map(
                int, row
            )
            assert (
                requantize_s32_to_s8(
                    value, multiplier, shift, zero_point, minimum, maximum
                )
                == expected
            )


def test_quantize_ties_saturation_and_dequantize() -> None:
    assert quantize_s8(0.5, 1.0) == 0
    assert quantize_s8(1.5, 1.0) == 2
    assert quantize_s8(2.5, 1.0) == 2
    assert quantize_s8(-1.5, 1.0) == -2
    assert quantize_s8(1000.0, 1.0) == 127
    assert quantize_s8(-1000.0, 1.0) == -128
    assert dequantize_s8(-4, 0.25, -2) == pytest.approx(-0.5)


def test_extreme_finite_quantization_saturates_safely() -> None:
    smallest_scale = float.fromhex("0x0.0000000000001p-1022")
    assert quantize_s8(sys.float_info.max, smallest_scale) == 127
    assert quantize_s8(-sys.float_info.max, smallest_scale) == -128
    assert quantize_s8(sys.float_info.max, 1.0) == 127
    assert quantize_s8(-sys.float_info.max, 1.0) == -128


def test_dequantize_rejects_nonfinite_result() -> None:
    with pytest.raises(ValueError, match="must be finite"):
        dequantize_s8(127, sys.float_info.max, -128)


def test_invalid_numeric_arguments() -> None:
    with pytest.raises(ValueError):
        round_divide_by_power_of_two(1, 63)
    with pytest.raises(ValueError):
        quantize_s8(float("nan"), 1.0)
    with pytest.raises(ValueError):
        quantize_s8(1.0, 0.0)
    with pytest.raises(ValueError):
        requantize_s32_to_s8(1, 1, 1, minimum=1, maximum=-1)
    with pytest.raises(ValueError):
        requantize_s32_to_s8(1, 0, 1)
    with pytest.raises(ValueError):
        requantize_s32_to_s8(1, 1, 1, zero_point=1)
    with pytest.raises(ValueError):
        requantize_s32_to_s8(1.0, 1, 1)
    with pytest.raises(ValueError):
        round_divide_by_power_of_two(1.5, 1)
    with pytest.raises(ValueError):
        quantize_s8(1.0, 1.0, zero_point=0.5)
    with pytest.raises(ValueError):
        dequantize_s8(1.5, 1.0)


def test_wrap_i32_boundaries() -> None:
    assert wrap_i32(0x7FFF_FFFF) == 0x7FFF_FFFF
    assert wrap_i32(0x8000_0000) == -0x8000_0000
    assert wrap_i32(0xFFFF_FFFF) == -1
    assert wrap_i32(-0x8000_0001) == 0x7FFF_FFFF


def test_gemm_known_values() -> None:
    a = np.array([[1, -2, 3], [4, 5, -6]], dtype=np.int8)
    b = np.array([[7, 8], [-9, 10], [11, -12]], dtype=np.int8)
    bias = np.array([100, -100], dtype=np.int32)
    expected = np.array([[158, -148], [17, 54]], dtype=np.int32)
    np.testing.assert_array_equal(gemm_s8s8_s32(a, b, bias), expected)


def test_gemm_shared_seeded_corpus() -> None:
    seed, cases, max_m, max_n, max_k = load_gemm_corpus_config()
    random = XorShift32(seed)
    for _ in range(cases):
        m = random.integer(1, max_m)
        n = random.integer(1, max_n)
        k = random.integer(1, max_k)
        a = np.array(
            [random.integer(-128, 127) for _ in range(m * k)],
            dtype=np.int8,
        ).reshape(m, k)
        b = np.array(
            [random.integer(-128, 127) for _ in range(k * n)],
            dtype=np.int8,
        ).reshape(k, n)
        bias = np.array(
            [wrap_i32(random.next_u32()) for _ in range(n)],
            dtype=np.int32,
        )
        expected = np.empty((m, n), dtype=np.int32)
        for row in range(m):
            for column in range(n):
                accumulator = int(bias[column])
                for inner in range(k):
                    accumulator = wrap_i32(
                        accumulator
                        + int(a[row, inner]) * int(b[inner, column])
                    )
                expected[row, column] = accumulator
        np.testing.assert_array_equal(gemm_s8s8_s32(a, b, bias), expected)


def test_gemm_rejects_bad_shapes_and_values() -> None:
    with pytest.raises(ValueError):
        gemm_s8s8_s32([[1, 2]], [[1, 2]])
    with pytest.raises(ValueError):
        gemm_s8s8_s32([[128]], [[1]])
    with pytest.raises(ValueError, match="must contain integers"):
        gemm_s8s8_s32([[1.5]], [[1]])
    with pytest.raises(ValueError, match="must contain integers"):
        gemm_s8s8_s32([["1"]], [[1]])
    with pytest.raises(ValueError, match="must contain integers"):
        gemm_s8s8_s32([[True]], [[1]])


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (np.empty((0, 1), dtype=np.int8), np.empty((1, 1), dtype=np.int8)),
        (np.empty((1, 1), dtype=np.int8), np.empty((1, 0), dtype=np.int8)),
        (np.empty((1, 0), dtype=np.int8), np.empty((0, 1), dtype=np.int8)),
    ],
    ids=["zero-m", "zero-n", "zero-k"],
)
def test_gemm_rejects_zero_dimensions(
    a: np.ndarray, b: np.ndarray
) -> None:
    with pytest.raises(ValueError, match="must be nonzero"):
        gemm_s8s8_s32(a, b)
