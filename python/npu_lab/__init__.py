"""Learning-oriented NPU simulation stack."""

from .numerics import (
    INT8_MAX,
    INT8_MIN,
    dequantize_s8,
    gemm_s8s8_s32,
    quantize_s8,
    requantize_s32_to_s8,
    round_divide_by_power_of_two,
    wrap_i32,
)

__all__ = [
    "INT8_MAX",
    "INT8_MIN",
    "dequantize_s8",
    "gemm_s8s8_s32",
    "quantize_s8",
    "requantize_s32_to_s8",
    "round_divide_by_power_of_two",
    "wrap_i32",
]
