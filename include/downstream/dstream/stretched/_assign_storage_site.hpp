#pragma once
#ifndef DOWNSTREAM_DSTREAM_STRETCHED__ASSIGN_STORAGE_SITE_HPP
#define DOWNSTREAM_DSTREAM_STRETCHED__ASSIGN_STORAGE_SITE_HPP

#include <algorithm>
#include <bit>
#include <cassert>
#include <concepts>
#include <optional>

#include "../../auxlib/DOWNSTREAM_UINT.hpp"
#include "./_has_ingest_capacity.hpp"

namespace downstream {
namespace dstream_stretched {

/**
 * Internal implementation of site selection algorithm for stretched curation.
 *
 * @param S Buffer size. Must be a power of two.
 * @param T Current logical time. Must be less than 2^S - 1.
 * @returns The selected storage site, or S if no site should be selected.
 *
 * @exceptsafe no-throw
 */
template <std::unsigned_integral UINT = DOWNSTREAM_UINT>
const UINT _assign_storage_site(const UINT S, const UINT T) {
  assert(dstream_stretched::has_ingest_capacity<UINT>(S, T));
  const UINT s = std::bit_width(S) - 1;
  const UINT t = std::max(std::bit_width(T) - s, UINT{0});  // Current epoch
  const UINT h = std::countr_zero(T + 1);  // Current hanoi value
  const UINT i =
      (h + 1) >= 64 ? 0
                    : (T >> (h + 1));  // Hanoi value incidence (i.e., num seen)

  const UINT blt = std::bit_width(t);  // Bit length of t
  const UINT t_floor = t <= 0 ? 0 : 1 << (std::bit_width(t) - 1);
  const bool epsilon_tau = t_floor << 1 > t + blt;  // Correction factor
  const UINT tau = blt - epsilon_tau;               // Current meta-epoch
  const UINT b =
      (S >> (tau + 1)) ? (S >> (tau + 1)) : 1;  // Num bunches available to h.v.
  if (i >= b) {  // If seen more than sites reserved to hanoi value...
    return S;    // ... discard without storing
  }

  const UINT b_l = i;  // Logical bunch index...
  // ... i.e., in order filled (increasing nestedness/decreasing init size r)

  // Need to calculate physical bunch index...
  // ... i.e., position among bunches left-to-right in buffer space
  const UINT v =
      std::bit_width(b_l);  // Nestedness depth level of physical bunch
  const UINT w =
      (S >> v) * (v != 0);  // Num bunches spaced between bunches in nest level
  const UINT o = w >> 1;  // Offset of nestedness level in physical bunch order
  const UINT b_l_floor = b_l <= 0 ? 0 : 1 << (std::bit_width(b_l) - 1);
  const UINT p = b_l - b_l_floor;  // Bunch position within nestedness level
  const UINT b_p = o + w * p;      // Physical bunch index...
  // ... i.e., in left-to-right sequential bunch order

  // Need to calculate buffer position of b_p'th bunch
  const bool epsilon_k_b = (b_l != 0);  // Correction factor for zeroth bunch...
  // ... i.e., bunch r=s at site k=0
  const UINT k_b = (b_p << 1) + std::popcount((S << 1) - b_p) - 1 -
                   epsilon_k_b;  // Site index of bunch

  return k_b + h;  // Calculate placement site...
                   // ... where h.v. h is offset within bunch
}

/**
 * Site selection algorithm for stretched curation.
 *
 * @param S Buffer size. Must be a power of two.
 * @param T Current logical time. Must be less than 2^S - 1.
 * @returns Selected site, if any. Returns nullopt if no site should be
 * selected.
 *
 * @exceptsafe no-throw
 */
template <std::unsigned_integral UINT = DOWNSTREAM_UINT>
const std::optional<UINT> assign_storage_site(const UINT S, const UINT T) {
  const UINT site = dstream_stretched::_assign_storage_site<UINT>(S, T);
  return site == S ? std::nullopt : std::optional<UINT>(site);
}

}  // namespace dstream_stretched
}  // namespace downstream

#endif  // DOWNSTREAM_DSTREAM_STRETCHED__ASSIGN_STORAGE_SITE_HPP
