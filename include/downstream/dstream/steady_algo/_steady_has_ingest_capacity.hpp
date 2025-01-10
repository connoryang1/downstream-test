#ifndef DOWNSTREAM_DSTREAM_STEADY_ALGO_STEADY_HAS_INGEST_CAPACITY_HPP
#define DOWNSTREAM_DSTREAM_STEADY_ALGO_STEADY_HAS_INGEST_CAPACITY_HPP

#include <bit>
#include <cassert>
#include <cstdint>

namespace downstream {
namespace dstream {
namespace steady_algo {

/**
 * Does this algorithm have the capacity to ingest a data item at logical time
 * T?
 *
 * @param S The number of buffer sites available.
 * @param T Queried logical time.
 * @returns Whether there is capacity to ingest at time T.
 *
 * @see steady_get_ingest_capacity How many data item ingestions does this
 * algorithm support?
 *
 * @exceptsafe no-throw
 */
const bool steady_has_ingest_capacity(const uint64_t S, const uint64_t T) {
  assert(T >= 0);
  return (std::popcount(S) == 1) and S > 1;
}

}  // namespace steady_algo
}  // namespace dstream
}  // namespace downstream

#endif  // DOWNSTREAM_DSTREAM_STEADY_ALGO_STEADY_HAS_INGEST_CAPACITY_HPP
