#include "npu/numerics.h"

#include <cmath>
#include <limits>
#include <stdexcept>

namespace npu {
namespace {

std::int64_t round_ties_to_even(double value) {
  const double lower_as_double = std::floor(value);
  const double fraction = value - lower_as_double;
  auto lower = static_cast<std::int64_t>(lower_as_double);
  if (fraction > 0.5 || (fraction == 0.5 && (lower & 1) != 0)) {
    return lower + 1;
  }
  return lower;
}

}  // namespace

std::int32_t wrap_i32(std::int64_t value) noexcept {
  constexpr std::uint64_t mask = 0xFFFF'FFFFULL;
  const auto bits = static_cast<std::uint32_t>(static_cast<std::uint64_t>(value) & mask);
  if (bits <= static_cast<std::uint32_t>(std::numeric_limits<std::int32_t>::max())) {
    return static_cast<std::int32_t>(bits);
  }
  return static_cast<std::int32_t>(
      static_cast<std::int64_t>(bits) - (static_cast<std::int64_t>(1) << 32));
}

std::int64_t round_divide_by_power_of_two(std::int64_t value, std::uint8_t shift) {
  if (shift > 62U) {
    throw std::invalid_argument("shift must be in [0, 62]");
  }
  if (shift == 0U) {
    return value;
  }

  const bool negative = value < 0;
  const std::uint64_t magnitude =
      negative ? static_cast<std::uint64_t>(-(value + 1)) + 1U
               : static_cast<std::uint64_t>(value);
  const std::uint64_t divisor = std::uint64_t{1} << shift;
  std::uint64_t quotient = magnitude / divisor;
  const std::uint64_t remainder = magnitude % divisor;
  const std::uint64_t twice_remainder = remainder << 1U;
  if (twice_remainder > divisor ||
      (twice_remainder == divisor && (quotient & 1U) != 0U)) {
    ++quotient;
  }
  const auto signed_quotient = static_cast<std::int64_t>(quotient);
  return negative ? -signed_quotient : signed_quotient;
}

std::int8_t requantize_s32_to_s8(
    std::int32_t value,
    std::int32_t multiplier,
    std::uint8_t shift,
    std::int8_t zero_point,
    std::int8_t minimum,
    std::int8_t maximum) {
  if (multiplier <= 0) {
    throw std::invalid_argument("multiplier must be in [1, INT32_MAX]");
  }
  if (zero_point != 0) {
    throw std::invalid_argument("ABI 1.0 zero point must be zero");
  }
  if (minimum > maximum) {
    throw std::invalid_argument("minimum must not exceed maximum");
  }
  const auto product = static_cast<std::int64_t>(value) * multiplier;
  auto result = round_divide_by_power_of_two(product, shift);
  if (result < minimum) {
    result = minimum;
  }
  if (result > maximum) {
    result = maximum;
  }
  return static_cast<std::int8_t>(result);
}

std::int8_t quantize_s8(double real_value, double scale, std::int8_t zero_point) {
  if (!std::isfinite(real_value)) {
    throw std::invalid_argument("real value must be finite");
  }
  if (!std::isfinite(scale) || scale <= 0.0) {
    throw std::invalid_argument("scale must be positive and finite");
  }
  const double scaled = real_value / scale;
  if (!std::isfinite(scaled)) {
    return scaled > 0.0 ? kInt8Max : kInt8Min;
  }

  const double upper =
      static_cast<double>(kInt8Max) - static_cast<double>(zero_point);
  const double lower =
      static_cast<double>(kInt8Min) - static_cast<double>(zero_point);
  if (scaled >= upper + 0.5) {
    return kInt8Max;
  }
  if (scaled <= lower - 0.5) {
    return kInt8Min;
  }

  auto result = round_ties_to_even(scaled) + zero_point;
  if (result < kInt8Min) {
    result = kInt8Min;
  }
  if (result > kInt8Max) {
    result = kInt8Max;
  }
  return static_cast<std::int8_t>(result);
}

double dequantize_s8(std::int8_t value, double scale, std::int8_t zero_point) {
  if (!std::isfinite(scale) || scale <= 0.0) {
    throw std::invalid_argument("scale must be positive and finite");
  }
  const double result =
      scale * (static_cast<int>(value) - static_cast<int>(zero_point));
  if (!std::isfinite(result)) {
    throw std::invalid_argument("dequantized result must be finite");
  }
  return result;
}

std::vector<std::int32_t> gemm_s8s8_s32(
    const std::vector<std::int8_t>& a,
    const std::vector<std::int8_t>& b,
    std::size_t m,
    std::size_t n,
    std::size_t k,
    const std::vector<std::int32_t>& bias) {
  if (m == 0U || n == 0U || k == 0U) {
    throw std::invalid_argument("GEMM dimensions M, N, and K must be nonzero");
  }
  if (m != 0U && k > std::numeric_limits<std::size_t>::max() / m) {
    throw std::overflow_error("A shape overflows size_t");
  }
  if (k != 0U && n > std::numeric_limits<std::size_t>::max() / k) {
    throw std::overflow_error("B shape overflows size_t");
  }
  if (a.size() != m * k || b.size() != k * n) {
    throw std::invalid_argument("GEMM storage size does not match shape");
  }
  if (!bias.empty() && bias.size() != n) {
    throw std::invalid_argument("bias must be empty or have N elements");
  }
  if (m != 0U && n > std::numeric_limits<std::size_t>::max() / m) {
    throw std::overflow_error("output shape overflows size_t");
  }

  std::vector<std::int32_t> output(m * n);
  for (std::size_t row = 0; row < m; ++row) {
    for (std::size_t column = 0; column < n; ++column) {
      std::int32_t accumulator = bias.empty() ? 0 : bias[column];
      for (std::size_t inner = 0; inner < k; ++inner) {
        const auto product =
            static_cast<std::int32_t>(a[row * k + inner]) *
            static_cast<std::int32_t>(b[inner * n + column]);
        accumulator = wrap_i32(static_cast<std::int64_t>(accumulator) + product);
      }
      output[row * n + column] = accumulator;
    }
  }
  return output;
}

}  // namespace npu
