# Song runtime regression expectations

The migrated tests execute `deadlib-lua` through the production Rust song
runtime. Their expected observations were captured independently from the
original Lua 5.1.5 host implementation, with every original comparison and
literal assertion still enabled during capture.

The initial capture profile is Windows/MSVC. Platform-dependent observations
need an independently reviewed capture for each supported profile.

The RNG fixtures retain complete floating-point bit patterns, input source
lengths and source digests. They cover shared namespaces, signed seed
conversion, rejected calls, independent song streams, nested snapshots,
collection and worker handoff. The existing recorded random probe and the
independent wall-clock seed check also remain enabled.

Clock fixtures preserve music-rate rounding, BPM changes, stops, delays, warps,
reentrant resets and captured getter ownership. Arrow fixtures also retain the
existing ITGmania numerical probes. Wrapper fixtures compare complete ordered
render states and callback transcripts, retaining error and release checks.

Actor fixtures preserve lifecycle transcripts, declaration observations, queue
limits, loading order and recovery assertions. Effect fixtures retain complete
render states, getter output, controlled clocks and playback transitions.
Message fixtures store dense relative delivery ranks; they contain no native
heap addresses. Natural Rust VM identity ordering is checked separately.

Sprite and sound fixtures retain texture metadata, animation, cache behavior,
event ordering and cleanup. Manager fixtures retain profile data, catalog
selection, all option levels, statistics, preferences, display state and theme
queries. Actor setter, generated player, screen UI and synthetic update-driver
fixtures retain their original Lua bodies, error checks and teardown checks.
Declaration fixtures bind their observations to the pinned upstream ActorDef
source and registration provenance. Screen request fixtures retain priorities,
transition queues, timestamps, publication ownership and hook observations.

The catalog metadata probes use an explicit virtual directory. File probes
normalize only their registered temporary directories, including the byte
lengths in serialized strings. Unregistered text, binary bytes, relative
suffixes, return arity and all non-path observations remain compared exactly.

Tests do not load another Lua runtime or regenerate expected data. The
historical implementation is used only in a separate ignored capture tool;
workspace manifests and normal test runs have no dependency on it.
