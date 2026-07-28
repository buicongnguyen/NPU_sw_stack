#ifndef NPU_NUMERICS_H
#define NPU_NUMERICS_H

#include <cstddef>
#include <cstdint>
#include <vector>

namespace npu {

constexpr std::int8_t kInt8Min = -128;
constexpr std::int8_t kInt8Max = 127;

std::int32_t wrap_i32(std::int64_t value) noexcept;

std::int64_t round_divide_by_power_of_two(std::int64_t value, std::uint8_t shift);

std::int8_t requantize_s32_to_s8(
    std::int32_t value,
    std::int32_t multiplier,
    std::uint8_t shift,
    std::int8_t zero_point = 0,
    std::int8_t minimum = kInt8Min,
    std::int8_t maximum = kInt8Max);

std::int8_t quantize_s8(double real_value, double scale, std::int8_t zero_point = 0);

double dequantize_s8(std::int8_t value, double scale, std::int8_t zero_point = 0);

std::vector<std::int32_t> gemm_s8s8_s32(
    const std::vector<std::int8_t>& a,
    const std::vector<std::int8_t>& b,
    std::size_t m,
    std::size_t n,
    std::size_t k,
    const std::vector<std::int32_t>& bias = {});

}  // namespace npu

#endif
