#include "npu/numerics.h"

#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void require(bool condition, const std::string& message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

template <typename Exception>
void require_throws(
    const std::function<void()>& operation,
    const std::string& message) {
  try {
    operation();
  } catch (const Exception&) {
    return;
  }
  throw std::runtime_error(message);
}

std::vector<std::int64_t> parse_csv_row(const std::string& line) {
  std::vector<std::int64_t> values;
  std::stringstream stream(line);
  std::string field;
  while (std::getline(stream, field, ',')) {
    values.push_back(std::stoll(field));
  }
  return values;
}

class XorShift32 {
 public:
  explicit XorShift32(std::uint32_t seed) : state_(seed) {
    require(seed != 0U, "xorshift32 seed must be nonzero");
  }

  std::uint32_t next_u32() {
    state_ ^= state_ << 13U;
    state_ ^= state_ >> 17U;
    state_ ^= state_ << 5U;
    return state_;
  }

  std::int32_t integer(std::int32_t minimum, std::int32_t maximum) {
    const auto span = static_cast<std::uint32_t>(
        static_cast<std::int64_t>(maximum) - minimum + 1);
    return minimum + static_cast<std::int32_t>(next_u32() % span);
  }

 private:
  std::uint32_t state_;
};

std::vector<std::int64_t> load_gemm_corpus_config() {
  const std::string path =
      std::string(NPU_SOURCE_DIR) + "/tests/fixtures/numerics/gemm-corpus.csv";
  std::ifstream file(path);
  require(file.good(), "failed to open GEMM corpus fixture");
  std::string line;
  while (std::getline(file, line)) {
    if (!line.empty() && line.front() != '#') {
      return parse_csv_row(line);
    }
  }
  throw std::runtime_error("GEMM corpus fixture has no configuration row");
}

void test_requantize_fixture() {
  const std::string path =
      std::string(NPU_SOURCE_DIR) + "/tests/fixtures/numerics/requantize.csv";
  std::ifstream file(path);
  require(file.good(), "failed to open requantize fixture");
  std::string line;
  std::size_t row = 0;
  while (std::getline(file, line)) {
    ++row;
    if (line.empty() || line.front() == '#') {
      continue;
    }
    const auto fields = parse_csv_row(line);
    require(fields.size() == 7U, "bad fixture field count");
    const auto actual = npu::requantize_s32_to_s8(
        static_cast<std::int32_t>(fields[0]),
        static_cast<std::int32_t>(fields[1]),
        static_cast<std::uint8_t>(fields[2]),
        static_cast<std::int8_t>(fields[3]),
        static_cast<std::int8_t>(fields[4]),
        static_cast<std::int8_t>(fields[5]));
    require(actual == fields[6], "requantize mismatch at fixture row " + std::to_string(row));
  }
}

void test_rounding() {
  require(npu::round_divide_by_power_of_two(1, 1) == 0, "+0.5 tie");
  require(npu::round_divide_by_power_of_two(3, 1) == 2, "+1.5 tie");
  require(npu::round_divide_by_power_of_two(5, 1) == 2, "+2.5 tie");
  require(npu::round_divide_by_power_of_two(-3, 1) == -2, "-1.5 tie");
  require(npu::round_divide_by_power_of_two(-5, 1) == -2, "-2.5 tie");
}

void test_quantize() {
  require(npu::quantize_s8(0.5, 1.0) == 0, "quantize +0.5");
  require(npu::quantize_s8(1.5, 1.0) == 2, "quantize +1.5");
  require(npu::quantize_s8(2.5, 1.0) == 2, "quantize +2.5");
  require(npu::quantize_s8(-1.5, 1.0) == -2, "quantize -1.5");
  require(npu::quantize_s8(1000.0, 1.0) == 127, "positive saturation");
  require(npu::quantize_s8(-1000.0, 1.0) == -128, "negative saturation");
  require(npu::dequantize_s8(-4, 0.25, -2) == -0.5, "dequantize");

  const double largest = std::numeric_limits<double>::max();
  const double smallest = std::numeric_limits<double>::denorm_min();
  require(
      npu::quantize_s8(largest, smallest) == 127,
      "division overflow saturation");
  require(
      npu::quantize_s8(-largest, smallest) == -128,
      "negative division overflow saturation");
  require_throws<std::invalid_argument>(
      [largest]() { static_cast<void>(npu::dequantize_s8(127, largest, -128)); },
      "nonfinite dequantization must be rejected");

  require_throws<std::invalid_argument>(
      []() { static_cast<void>(npu::requantize_s32_to_s8(1, 0, 1)); },
      "zero multiplier must be rejected");
  require_throws<std::invalid_argument>(
      []() { static_cast<void>(npu::requantize_s32_to_s8(1, 1, 1, 1)); },
      "nonzero ABI zero point must be rejected");
}

void test_wrap() {
  require(npu::wrap_i32(0x7FFF'FFFFLL) == 0x7FFF'FFFF, "max int32");
  require(
      npu::wrap_i32(0x8000'0000LL) ==
          std::numeric_limits<std::int32_t>::min(),
      "min int32");
  require(npu::wrap_i32(0xFFFF'FFFFLL) == -1, "minus one");
  require(npu::wrap_i32(-0x8000'0001LL) == 0x7FFF'FFFF, "negative wrap");
}

void test_gemm() {
  const std::vector<std::int8_t> a = {1, -2, 3, 4, 5, -6};
  const std::vector<std::int8_t> b = {7, 8, -9, 10, 11, -12};
  const std::vector<std::int32_t> bias = {100, -100};
  const std::vector<std::int32_t> expected = {158, -148, 17, 54};
  require(npu::gemm_s8s8_s32(a, b, 2, 2, 3, bias) == expected, "known GEMM");

  require_throws<std::invalid_argument>(
      []() {
        static_cast<void>(
            npu::gemm_s8s8_s32({}, {1}, 0, 1, 1));
      },
      "zero M must be rejected");
  require_throws<std::invalid_argument>(
      []() {
        static_cast<void>(
            npu::gemm_s8s8_s32({1}, {}, 1, 0, 1));
      },
      "zero N must be rejected");
  require_throws<std::invalid_argument>(
      []() {
        static_cast<void>(
            npu::gemm_s8s8_s32({}, {}, 1, 1, 0));
      },
      "zero K must be rejected");
}

void test_gemm_shared_seeded_corpus() {
  const auto config = load_gemm_corpus_config();
  require(config.size() == 5U, "bad GEMM corpus configuration");
  require(
      config[0] > 0 && config[0] <= 0xFFFF'FFFFLL,
      "GEMM corpus seed must fit nonzero uint32");
  require(config[1] > 0, "GEMM corpus case count must be positive");
  require(
      config[2] > 0 && config[3] > 0 && config[4] > 0,
      "GEMM corpus dimension limits must be positive");
  XorShift32 random(static_cast<std::uint32_t>(config[0]));
  const auto cases = static_cast<std::size_t>(config[1]);
  const auto max_m = static_cast<std::int32_t>(config[2]);
  const auto max_n = static_cast<std::int32_t>(config[3]);
  const auto max_k = static_cast<std::int32_t>(config[4]);

  for (std::size_t index = 0; index < cases; ++index) {
    const auto m = static_cast<std::size_t>(random.integer(1, max_m));
    const auto n = static_cast<std::size_t>(random.integer(1, max_n));
    const auto k = static_cast<std::size_t>(random.integer(1, max_k));
    std::vector<std::int8_t> a(m * k);
    std::vector<std::int8_t> b(k * n);
    std::vector<std::int32_t> bias(n);
    std::vector<std::int32_t> expected(m * n);

    for (auto& value : a) {
      value = static_cast<std::int8_t>(random.integer(-128, 127));
    }
    for (auto& value : b) {
      value = static_cast<std::int8_t>(random.integer(-128, 127));
    }
    for (auto& value : bias) {
      value = npu::wrap_i32(static_cast<std::int64_t>(random.next_u32()));
    }

    for (std::size_t row = 0; row < m; ++row) {
      for (std::size_t column = 0; column < n; ++column) {
        auto accumulator = bias[column];
        for (std::size_t inner = 0; inner < k; ++inner) {
          const auto product =
              static_cast<std::int32_t>(a[row * k + inner]) *
              static_cast<std::int32_t>(b[inner * n + column]);
          accumulator =
              npu::wrap_i32(static_cast<std::int64_t>(accumulator) + product);
        }
        expected[row * n + column] = accumulator;
      }
    }

    require(
        npu::gemm_s8s8_s32(a, b, m, n, k, bias) == expected,
        "shared GEMM corpus mismatch at case " + std::to_string(index));
  }
}

}  // namespace

int main() {
  try {
    test_rounding();
    test_requantize_fixture();
    test_quantize();
    test_wrap();
    test_gemm();
    test_gemm_shared_seeded_corpus();
    std::cout << "C++ numerics tests passed\n";
    return EXIT_SUCCESS;
  } catch (const std::exception& error) {
    std::cerr << "C++ numerics test failure: " << error.what() << '\n';
    return EXIT_FAILURE;
  }
}
