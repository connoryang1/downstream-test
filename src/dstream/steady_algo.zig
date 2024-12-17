const std = @import("std");

const aux = @import("../_auxlib.zig");

pub fn has_ingest_capacity(S: u32, T: u32) bool {
    _ = T;
    return (@popCount(S) == 1) and S > 1;
}

pub fn assign_storage_site(S: u32, T: u32) u32 {
    std.debug.assert(has_ingest_capacity(S, T));

    const s = aux.bit_length(S) - 1;
    const blt = aux.bit_length(T);
    const t = aux.floor_subtract(blt, s); // Current epoch
    const h = @ctz(T + 1); // Current hanoi value

    // Hanoi value incidence (i.e., num seen)
    const i = T >> @intCast(h + 1);

    // Num full-bunch segments
    const j = aux.bit_floor(i) -% 1;
    const B = aux.bit_length(j); // Num full bunches
    // Bunch position
    var k_b = aux.overflow_shl(1, B) *% (s + 1 -% B);
    // substituting t = s - blt into h + 1 - t
    var w = h + s + 1 -% blt; // Segment width
    var o = w *% (i -% (j +% 1)); // Within-bunch offset

    const is_zeroth_bunch = i == 0;
    k_b = if (!is_zeroth_bunch) k_b else 0;
    o = if (!is_zeroth_bunch) o else 0;
    w = if (!is_zeroth_bunch) w else s + 1;

    const p = h % @max(w, 1); // Within-segment offset, avoiding divide by zero

    // handle discard without storing for non-top n(T) hanoi value...
    return if (h >= t) k_b + o + p else S;
}
