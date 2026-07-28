#include "npu/numerics.h"

#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
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

std::vector<std::int64_t> parse_csv_row(const std::string& line) {
  std::vector<std::int64_t> values;
  std::stringstream stream(line);
  std::string field;
  while (std::getline(stream, field, ',')) {
    values.push_back(std::stoll(field));
  }
  return values;
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
}

void test_wrap() {
  require(npu::wrap_i32(0x7FFF'FFFFLL) == 0x7FFF'FFFF, "max int32");
  require(npu::wrap_i32(0x8000'0000LL) == static_cast<std::int32_t>(0x8000'0000U), "min int32");
  require(npu::wrap_i32(0xFFFF'FFFFLL) == -1, "minus one");
  require(npu::wrap_i32(-0x8000'0001LL) == 0x7FFF'FFFF, "negative wrap");
}

void test_gemm() {
  const std::vector<std::int8_t> a = {1, -2, 3, 4, 5, -6};
  const std::vector<std::int8_t> b = {7, 8, -9, 10, 11, -12};
  const std::vector<std::int32_t> bias = {100, -100};
  const std::vector<std::int32_t> expected = {158, -148, 17, 54};
  require(npu::gemm_s8s8_s32(a, b, 2, 2, 3, bias) == expected, "known GEMM");
}

}  // namespace

int main() {
  try {
    test_rounding();
    test_requantize_fixture();
    test_quantize();
    test_wrap();
    test_gemm();
    std::cout << "C++ numerics tests passed\n";
    return EXIT_SUCCESS;
  } catch (const std::exception& error) {
    std::cerr << "C++ numerics test failure: " << error.what() << '\n';
    return EXIT_FAILURE;
  }
}
