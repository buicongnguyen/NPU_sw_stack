from __future__ import annotations

import csv
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


def test_invalid_numeric_arguments() -> None:
    with pytest.raises(ValueError):
        round_divide_by_power_of_two(1, 63)
    with pytest.raises(ValueError):
        quantize_s8(float("nan"), 1.0)
    with pytest.raises(ValueError):
        quantize_s8(1.0, 0.0)
    with pytest.raises(ValueError):
        requantize_s32_to_s8(1, 1, 1, minimum=1, maximum=-1)


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


def test_gemm_seeded_random_against_int64_oracle() -> None:
    random = np.random.default_rng(0x4E5055)
    for _ in range(1000):
        m = int(random.integers(1, 6))
        n = int(random.integers(1, 6))
        k = int(random.integers(1, 12))
        a = random.integers(-128, 128, size=(m, k), dtype=np.int16).astype(np.int8)
        b = random.integers(-128, 128, size=(k, n), dtype=np.int16).astype(np.int8)
        bias = random.integers(-10000, 10001, size=n, dtype=np.int32)
        expected = a.astype(np.int64) @ b.astype(np.int64) + bias.astype(np.int64)
        expected = (((expected + (1 << 31)) % (1 << 32)) - (1 << 31)).astype(
            np.int32
        )
        np.testing.assert_array_equal(gemm_s8s8_s32(a, b, bias), expected)


def test_gemm_rejects_bad_shapes_and_values() -> None:
    with pytest.raises(ValueError):
        gemm_s8s8_s32([[1, 2]], [[1, 2]])
    with pytest.raises(ValueError):
        gemm_s8s8_s32([[128]], [[1]])
