#ifndef DOWNSTREAM_DSTREAM_STEADY_ALGO_STEADY_GET_INGEST_CAPACITY_HPP
#define DOWNSTREAM_DSTREAM_STEADY_ALGO_STEADY_GET_INGEST_CAPACITY_HPP

#include <bitset>
#include <cstdint>
#include <bit>
#include <optional>

namespace downstream {
namespace dstream {
namespace steady_algo {

const std::optional<uint64_t> steady_get_ingest_capacity(const uint64_t S) {
  const bool surface_size_ok = std::has_single_bit(S) && S > 1;
  return surface_size_ok ? std::nullopt : std::optional<uint64_t>(0);
}

} // namespace steady_algo
} // namespace dstream
} // namespace downstream

#endif // DOWNSTREAM_DSTREAM_STEADY_ALGO_STEADY_GET_INGEST_CAPACITY_HPP