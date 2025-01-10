#pragma once
#ifndef DOWNSTREAM_DSTREAM_STEADY__ASSIGN_STORAGE_SITE_HPP
#define DOWNSTREAM_DSTREAM_STEADY__ASSIGN_STORAGE_SITE_HPP

#include <algorithm>
#include <bit>
#include <cassert>
#include <concepts>
#include <optional>

#include "../../auxlib/DOWNSTREAM_UINT.hpp"
#include "./_has_ingest_capacity.hpp"

namespace downstream {
namespace dstream_steady {

/**
 * Internal implementation of site selection algorithm for steady curation.
 *
 * @param S Buffer size. Must be a power of two.
 * @param T Current logical time.
 * @returns The selected storage site, or S if no site should be selected.
 *
 * @exceptsafe no-throw
 */
template <std::unsigned_integral UINT = DOWNSTREAM_UINT>
const UINT _assign_storage_site(const UINT S, const UINT T) {
  assert(dstream_steady::has_ingest_capacity<UINT>(S, T));
  const UINT s = std::bit_width(S) - 1;
  const UINT blT = std::bit_width(T);
  const UINT t = blT - std::min(s, blT);   // Current epoch
  const UINT h = std::countr_zero(T + 1);  // Current hanoi value
  if (h < t) {                             // If not a top n(T) hanoi value...
    return S;                              // ...discard without storing
  }
  const UINT i = T >> (h + 1);  // Hanoi value incidence (i.e., num seen)
  UINT k_b, o, w;  // Bunch position, within-bunch offset, segment width
  if (i == 0) {    // Special case the 0th bunch
    k_b = 0;       // Bunch position
    o = 0;         // Within-bunch offset
    w = s + 1;     // Segment width
  } else {
    const UINT j = std::bit_floor(i) - 1;  // Num full-bunch segments
    const UINT B = std::bit_width(j);      // Num full bunches
    k_b = (1 << B) * (s - B + 1);          // Bunch position
    // substituting t = s - blT into h + 1 - t
    w = h + s + 1 - blT;  // Segment width
    o = w * (i - j - 1);  // Within-bunch offset
  }
  assert(w > 0);
  const UINT p = h % w;  // Within-segment offset
  return k_b + o + p;    // Calculate placement site
}

/**
 * Site selection algorithm for steady curation.
 *
 * @param S Buffer size. Must be a power of two.
 * @param T Current logical time.
 * @returns Selected site, if any. Returns nullopt if no site should be
 * selected.
 *
 * @exceptsafe no-throw
 */
template <std::unsigned_integral UINT = DOWNSTREAM_UINT>
const std::optional<UINT> assign_storage_site(const UINT S, const UINT T) {
  const UINT site = dstream_steady::_assign_storage_site<UINT>(S, T);
  return site == S ? std::nullopt : std::optional<UINT>(site);
}

}  // namespace dstream_steady
}  // namespace downstream

#endif  // DOWNSTREAM_DSTREAM_STEADY__ASSIGN_STORAGE_SITE_HPP
