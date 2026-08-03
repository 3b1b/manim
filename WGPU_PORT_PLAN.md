# Porting ManimGL from OpenGL to wgpu

A plan, written against the tree as of #2482 ("Cleaner rendering logic").

## Summary

The port is smaller than it looks, for one reason: #2482 already moved the renderer onto
the two patterns wgpu is built around. Every vertex shader now reads its own records out
of a buffer indexed by the vertex id, rather than being handed attributes or expanded by a
geometry shader, and every mobject's uniforms now travel as one std140 block rather than
one value at a time. Those are not GL techniques that happen to survive the move; they are
what wgpu asks for. What remains is mostly the imperative state-setting around draws,
which becomes declarative pipeline objects, and a translation of ~1200 lines of GLSL into
WGSL.

The genuinely hairy part is not the drawing. It is the window: manim's interactive model is
that Python is in charge and the window is subordinate, and every GPU-canvas framework in
the ecosystem inverts that. The plan below keeps manim in charge and takes the window
back, which also drops three dependencies.

Two things this plan deliberately refuses:

- **No dual-backend abstraction.** A `Renderer` interface with GL and wgpu implementations
  behind it would be exactly the bespoke code we are trying to delete, and would freeze
  every GL-shaped assumption into the interface. Keep the GL renderer alive on a branch for
  A/B comparison during the port, then delete it.
- **No compatibility shim for user GLSL.** `set_color_by_code` takes GLSL today. It takes
  WGSL after. Nothing in the `videos` repo currently calls it, but three scenes name a
  `shader_folder`: `_2021/newton_fractal.py` and `_2021/holomorphic_dynamics.py` point at
  manimlib's own fractal shaders, and `_2024/holograms/diffraction.py` ships its own
  `diffraction_shader/` pair. Those three get ported by hand.

## Where the OpenGL actually lives

Worth stating precisely, because it bounds the work.

| File | GL calls | Role |
|---|---|---|
| `manimlib/shader_wrapper.py` | 22 | buffers, buffer-as-texture aliasing, stencil/mask/cull state |
| `manimlib/camera/camera.py` | 14 | framebuffers, depth-stencil attachment, blits, clip-plane enables |
| `manimlib/utils/shaders.py` | 6 | uniform block introspection, one sampler workaround |
| `manimlib/window.py` | — | `moderngl_window` + pyglet |
| `manimlib/__init__.py` | — | one line setting `OpenGL.ERROR_CHECKING` |
| `scene.py`, `interactive_scene.py`, `interactive.py` | — | pyglet key constants only |

That is the whole surface. Nothing in `mobject/`, `animation/`, `utils/` (bezier, colors,
space ops), the SVG/Tex/Text pipeline, or the file writer touches the GPU. The 23k lines of
manimlib are, to a first approximation, untouched by this.

The shader corpus is ~1200 lines across 14 vertex/fragment pairs and 12 inserts. The two
largest single files are `newton_fractal/frag.glsl` (145) and
`inserts/get_xyz_to_uv.glsl` (100).

---

## Design decisions

### 1. WGSL, keeping the `#INSERT` preprocessor

wgpu-py takes WGSL source or SPIR-V. Routing GLSL through naga's GLSL frontend is not
exposed through the Python API in any way worth depending on, and precompiling to SPIR-V
means adding a shader toolchain to the build. So: translate to WGSL.

Everything about `utils/shaders.py`'s file half survives verbatim. `#INSERT` is plain text
substitution and does not care what language it is substituting. `set_color_by_code` and
`code_replacements` are regex over source text and do not care either. Rename the files to
`.wgsl` and that machinery is done.

WGSL makes two inserts *better*:

- **Varyings become a shared struct.** Today `stroke/vert.glsl` declares `out vec4 color;
  out float dist_to_aaw; out float half_width_to_aaw;` and `stroke/frag.glsl` re-declares
  the same three as `in`. In WGSL there is one `VertexOutput` struct, which lives in an
  insert included by both stages. The duplication that exists today disappears, and drift
  between the two stages becomes a compile error rather than a silent mismatch.
- **`read_data.glsl` mostly dissolves.** `uniform samplerBuffer Data` plus four
  `texelFetch` accessors become `var<storage, read> data: array<f32>` plus direct indexing.
  36 lines → ~12.

### 2. The data buffer is a storage buffer, still read as flat floats

Read-only storage buffers are visible to the vertex stage in WebGPU, so the buffer-aliased-
as-a-texture trick from #2482 becomes a plain binding. This is what deletes `import
OpenGL.GL` from `shader_wrapper.py`: `init_data_texture`'s raw `glGenTextures`/`glTexBuffer`
and the `set_program_sampler` driver workaround both existed only to serve that alias.

Tempting next step: generate a WGSL `struct` from the mobject's dtype so shaders write
`data[record].point` instead of `read_vec3(record, DATA_OFFSET_point)`. **Don't.** WGSL's
storage layout rules align `vec3<f32>` to 16 bytes, so a struct would force every 3-float
field in every data dtype to be padded to 4 — and `point` is in every record of every
mobject. Keep the generated `DATA_STRIDE`/`DATA_OFFSET_*` constants and flat-float reads
exactly as they are now. The numpy dtypes stay packed, and the Python side of the layout
codegen (`get_data_layout_code`) is unchanged.

### 3. Render state becomes a small table of named pipeline states

This is the central structural change. Today state is set imperatively around draws:
`glStencilOpSeparate`, `glColorMask`, `glDepthMask`, `glCullFace`, `ctx.enable(DEPTH_TEST)`.
In wgpu all of it is baked into a `RenderPipeline` at creation time.

The saving grace is that manim uses very few combinations. Enumerate them once, as a
module-level table:

| Name | Depth | Stencil | Color write | Cull |
|---|---|---|---|---|
| `default` | off | off | on | none |
| `depth` | test+write | off | on | none |
| `winding_count` | off, no write | always; front `increment-wrap`, back `decrement-wrap` | **off** | none |
| `fill_border` | per mobject | `equal` 0, keep | on | none |
| `winding_cover` | per mobject | `not-equal` 0, zero on pass and on depth-fail | on | none |
| `cull_front` / `cull_back` | per mobject | off | on | front / back |

`get_pipeline(shader_key, state_name, sample_count)` behind an `lru_cache`, mirroring
today's `get_shader_program`. `VShaderWrapper.render_fill`'s forty lines of state fiddling
collapse to three `set_pipeline` calls plus one `set_stencil_reference`. The comments
explaining *why* stencil-then-cover works are the valuable part of that method and they all
stay; only the poking goes.

Note the depth/stencil format: `depth24plus-stencil8` is a required WebGPU format, so
`Camera.attach_depth_stencil` — thirty lines of raw GL renderbuffer creation with a
`depth_stencil_rbos` list held only to defeat garbage collection, written because moderngl
cannot make a combined attachment — is deleted outright.

### 4. `is_fill_border` becomes two pipelines, not a uniform

It is the last remaining per-draw loose uniform. Two options, both fine:

- **Text substitution** (recommended): compile the stroke shader twice from the same source
  with `is_fill_border` substituted as a `const`. The `replace_code` machinery for this
  already exists and is already used by `VShaderWrapper`.
- WGSL `override` constants with `constants` passed at pipeline creation. Tidier, but
  wgpu-native's override support has been uneven; verify before relying on it.

Either way, `set_program_uniform` has no remaining callers.

### 5. Three bind groups, matching three lifetimes

```
group(0)  frame       view matrix, frame_rescale_factors, pixel_size,
                      camera_position, light_position     — written once per frame
group(1)  mobject     the std140 block from #2482          — written when it changes
group(2)  resources   data storage buffer + textures/samplers — rebuilt on resize
```

Group 0 is where the biggest deletion lives. Today, uniforms shared by every program are
pushed into every program individually, guarded by a mirror of previously-set values to
avoid redundant driver calls, with a separate set of names each program turned out not to
have. That is `ALL_PROGRAMS`, `SHARED_UNIFORMS`, `PROGRAM_UNIFORM_MIRRORS`,
`PROGRAM_ABSENT_UNIFORMS`, `set_shared_uniforms`, `get_shared_uniform`,
`set_program_uniform`, `set_program_sampler` — roughly 110 lines of `utils/shaders.py`, all
of which exist because GL has no way to say "these values hold for everything." wgpu does:
one buffer, one bind group, written once a frame.

So **give the camera the same treatment #2482 gave mobjects**: its uniforms become a
`Uniforms` block built by the existing `uniform_block_dtype`. `Camera.refresh_uniforms`
stops building a dict of tuples and writes into an array. This is worth doing on `master`
before any wgpu work — it is a real simplification under GL too (see Phase 0b).

One consequence to handle: `SurfaceShaderWrapper.order_triangles_by_depth` reaches for
`get_shared_uniform("camera_position")` through the module-global. With the globals gone it
reads it off the frame uniforms handed to it, which is more honest anyway.

While we're here: `check_uniform_block`'s fifty lines of `glGetActiveUniform` introspection,
which exists to catch a shader's declared block drifting from the mobject's dtype, has no
wgpu equivalent — and does not need one. Generate the WGSL struct declaration *from* the
dtype (`uniform_block_code` already prints it) and `#INSERT` the generated text. Drift
becomes impossible by construction and the check is deleted. The cost is that the comments
currently living in `vmobject_uniforms.glsl` move next to the member list in Python, which
is arguably where they belong, since that is where the layout is actually decided.

### 6. One render target, and the window is a place to present it

Today: three framebuffers (`fbo_for_files`, `draw_fbo`, `window_fbo`), a `use_window_fbo`
toggle, `detect_framebuffer(0)`, and a two-blit-two-swap dance whose comments explain that
multisampled buffers cannot be blit with rescaling.

New: one color texture plus one `depth24plus-stencil8` texture. Every frame renders into
them, whatever the destination. Then:

- **With a window:** one extra draw of that texture onto the surface texture — a fullscreen
  triangle with a linear sampler, ~15 lines of WGSL, structurally the same as the existing
  `image` shader. MSAA resolves through the color attachment's `resolve_target`, which is
  what the two-blit workaround was emulating.
- **Writing a file:** `copy_texture_to_buffer` → map → `np.frombuffer`. One wrinkle:
  `bytes_per_row` must be a multiple of 256, and low quality (854 × 4 = 3416) is not, so the
  readback allocates padded rows and slices. Five lines, in one place.
- **`-s` and `get_image`:** the same readback path. `Scene.get_image`'s
  `use_window_fbo(False)` / recapture / `use_window_fbo(True)` dance goes away.

The `use_window_fbo` *policy* — preview at window size when not writing, at output
resolution when writing — is worth keeping, since rendering 4K to downscale into a small
window is a real cost. But it stops being "which of three framebuffers am I bound to" and
becomes "what size is my one texture", recreated on resize. Plumbing deleted, behavior kept.

`glClear(GL_STENCIL_BUFFER_BIT)` at the top of `capture` becomes the render pass's
`stencil_load_op: "clear"`.

### 7. One render pass per frame, and writes strictly before it

This is the one place where a naive port produces something *slower* than today, so it is
worth stating loudly. Beginning a render pass per mobject with `load_op: "load"` would be
disastrous on tile-based GPUs — which is to say, on exactly the Apple hardware this port is
for. The whole frame must be a single render pass.

It can be, because everything the fill algorithm needs between draws is either pipeline
state (stencil ops, color mask, depth mask) or a pass command (`set_stencil_reference`).
Nothing requires a pass break. The frame becomes one long sequence of
`set_pipeline` / `set_bind_group` / `draw`, which is strictly less driver state churn than
today.

The constraint this imposes: **all buffer writes happen before the pass opens.** Queue
writes issued while a pass is recording have subtle ordering semantics, and
`order_triangles_by_depth` writes an index buffer mid-frame. Fortunately the code is
already shaped for this — `pre_render` (all the writes) and `render` (all the draws) are
already separate methods. `Mobject.render` becomes two walks of the tree: one calling
`pre_render` on every wrapper with no pass open, then the pass, then one calling `render`.
That is a handful of lines and it falls straight out of the existing structure.

### 8. `Renderer` replaces the bare `ctx` passed around

`mobject.render(ctx)` currently takes a `moderngl.Context`. Under wgpu the callee needs the
device, the queue, the pipeline cache, the frame bind group, and the open pass. Passing five
things is worse than passing one:

```python
class Renderer:
    device, queue          # wgpu handles
    frame_uniforms         # the group(0) Uniforms block + buffer + bind group
    get_pipeline(...)      # the lru_cache from decision 3
    pass_                  # the open render pass, during the draw walk
```

`mobject.render(renderer)`, `ShaderWrapper(renderer, ...)`. Mechanically a rename across
`mobject.py`, `vectorized_mobject.py`, `surface.py`; conceptually a better seam than `ctx`,
since it is the natural home for the frame-level bind group and the pipeline cache.

---

## The window

The property to preserve is easy to state and easy to lose: **manim's Python code drives the
loop.** `self.wait()` blocks in a loop calling `update_frame`. `self.embed()` hands control
to IPython, which calls `play()` whenever the user types it. `update_frame` pumps events
itself (`window._window.dispatch_events()`) and sleeps to pace against wall-clock time.
`interact()` spins until the window closes.

`rendercanvas` — the GUI layer split out of wgpu-py, with glfw/Qt/wx/jupyter/offscreen
backends — is built the other way around: you register a draw callback and call
`loop.run()`. Adopting it means either restructuring manim's whole interactive model around
callbacks, or reaching into private API to pump it manually. Both are the bespoke-code trap.

**So use glfw directly and write manim's window ourselves.** glfw is a library rather than a
framework, and it maps onto what manim already does:

| Today | With glfw |
|---|---|
| `window._window.dispatch_events()` | `glfw.poll_events()` |
| `moderngl_window` `on_mouse_*` / `on_key_*` overrides | `glfw.set_*_callback`, 1:1 |
| `screeninfo.get_monitors()` | `glfw.get_monitors()` + `get_monitor_workarea` |
| `focus()` — hide then show, "pyglet's `activate()` didn't work" | `glfw.focus_window` |
| `to_default_position()` — resize by one pixel to force a redraw | not needed |
| `mglw.WindowConfig` / `Timer` / `activate_context` ceremony | not needed |

`window.py` goes from 242 lines of `moderngl_window` subclass plus workarounds to roughly
150 lines of direct calls. `moderngl_window`, `pyglet`, and `screeninfo` all drop out.

**The one API detail to spike first** is how wgpu-py gets a surface from a glfw window
without taking rendercanvas's loop. wgpu-py's canvas context expects a small protocol
(present info, physical size, and so on); implementing that protocol on our own `Window` is
the intended seam, but the exact shape has churned across wgpu-py versions. This is item
one of the Phase 1 spike, and the answer determines whether `window.py` is 150 lines or 200.

### Owning the input vocabulary

Three files import `from pyglet.window import key as PygletWindowKeys` and use it in two
ways: `ord(char)` for letters, and named constants for arrows/modifiers. glfw's letter
codes are `ord(uppercase)` and its modifier bits differ, so a mapping is needed regardless.

Take the opportunity: a `manimlib/event_keys.py` defining manim's own `Keys` and `Mods`,
with the window translating from whatever it is built on. Besides removing the pyglet
coupling from `scene.py`, `interactive_scene.py` and `interactive.py`, it collapses the
`(modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL))` idiom — which
appears about ten times — into one `Mods.CTRL_OR_CMD`. This lands on `master` today, on its
own merits, with no wgpu in sight.

---

## Shader translation notes

Mechanical, but these five will bite if not planned for.

**Depth range.** WebGPU's NDC z is `[0, 1]`; GL's is `[-1, 1]`. `emit_gl_Position.glsl`
currently ends with `result.w = 1.0 - result.z; result.z *= -0.1;` — that mapping has to be
rederived. It is the single most delicate change in the port, since getting it wrong makes
every 3D scene subtly wrong rather than obviously broken. Mitigation: it lives in exactly
one insert, shared by every shader. Change it once, validate against a `ThreeDScene` with
overlapping surfaces.

**Clip planes.** Core WebGPU has no `gl_ClipDistance` — wgpu exposes a native
`CLIP_DISTANCES` feature but not on the Metal backend, which is the whole point of the
exercise. Replace with: pack the four distances into one `vec4` in the vertex output struct
(one interpolation slot, not four), and `discard` in the fragment shader when any component
is negative. An insert function `clip_test(in)` called at the top of each fragment `main`.

Two things to note. `discard` suppresses stencil writes as well as color writes, which is
exactly right for the winding-count pass. And hardware clipping cuts geometry at the plane
while `discard` cuts per-pixel — visually identical here, and this can be validated under GL
before the port (Phase 0c), which is much easier than debugging it afterwards.

**Framebuffer orientation.** WebGPU textures have their origin at the top-left. The `[::-1]`
row flip in `get_pixel_array` and the `-1` orientation argument in `Image.frombytes` go
away; the `v` coordinate in `image` and `textured_surface` flips.

**Strict typing.** WGSL has no implicit int→float conversion. The bezier shaders lean on
GLSL's looseness constantly (`min(int(alpha * 8), 7)`, `float(index) / float(n_steps - 1)`
next to `POLYLINE_FACTOR * sqrt(area)`). Nothing hard, but it touches nearly every line of
the two largest shaders.

**Const arrays and entry points.** `const vec2 CORNERS[6] = vec2[6](...)` becomes
`const CORNERS = array<vec2f, 6>(...)`; `gl_VertexID` becomes `@builtin(vertex_index)`;
`gl_Position` becomes a returned `@builtin(position)`. The "collapse all six corners onto one
point to leave nothing to rasterize" idiom for blanking a curve works identically.

Suggested translation order, each validated on screen before moving on:

1. `image` — smallest thing that exercises the whole chain (storage buffer, uniform block, texture, sampler)
2. `true_dot` — adds a second uniform block shape
3. `surface`, `textured_surface` — adds depth, culling, two-pass draw, `sort_to_camera`
4. `quadratic_bezier/fill` — adds stencil-then-cover, the highest-risk pipeline state
5. `quadratic_bezier/stroke` — largest, and the fill's border depends on it
6. `mandelbrot_fractal`, `newton_fractal`, and the `videos` repo's `diffraction_shader`

---

## Phasing

### Phase 0 — land on `master`, no wgpu involved

Each of these is a genuine improvement under GL, reviewable on its own, and each shrinks the
diff of everything after. This phase is most of the risk reduction available.

- **0a. Input vocabulary.** `event_keys.py`; drop pyglet imports from the three scene/mobject
  files; collapse the `CTRL_OR_CMD` repetition.
- **0b. Camera uniforms as a block.** `Camera.refresh_uniforms` writes a `Uniforms` array
  built by `uniform_block_dtype`, uploaded as a UBO at a second binding. Deletes the
  uniform-mirror machinery *today*.
- **0c. Clip planes via fragment discard.** Removes the four `glEnable(GL_CLIP_DISTANCE*)`
  calls and the `gl_ClipDistance` writes. A/B testable against current output.
- **0d. `Renderer` seam and the state table.** Introduce `Renderer` wrapping `ctx`; change
  `render(ctx)` → `render(renderer)`; move stencil/mask/cull poking out of the wrappers into
  the named-state table (still calling `gl.*` underneath); split the frame into
  pre-render-everything then draw-everything.

After 0a–0d, GL is confined to `Renderer`, `Camera`, and the shader files.

### Phase 1 — spike, one throwaway file

Retire the API uncertainties before committing to anything: glfw window → wgpu surface
without rendercanvas's loop; a read-only storage buffer indexed from the vertex stage; a
uniform block matching a numpy dtype; stencil-then-cover with `increment-wrap` /
`decrement-wrap` on a hand-made shape; `copy_texture_to_buffer` readback with row padding;
and the depth remap. A few hundred lines, deleted afterwards. Pin the wgpu-py version here —
it is pre-1.0 and renames things.

### Phase 2 — the port

- **2a.** `window.py` on glfw, behind Phase 0a's vocabulary, so nothing above it changes.
- **2b.** `Renderer` grows its wgpu implementation: device, queue, pipeline cache, bind
  group layouts, render target, present pipeline, readback.
- **2c.** Shaders to WGSL in the order above.
- **2d.** Delete: the GL imports in `shader_wrapper.py`, `attach_depth_stencil`, the blit
  chain, `use_window_fbo`, the uniform mirrors, `check_uniform_block`, `set_program_*`,
  `read_data.glsl`'s texelFetch layer, and `OpenGL.ERROR_CHECKING` from `__init__.py`.

### Phase 3 — validation

There is no test suite, so build the one thing that makes a port like this safe and which is
worth having regardless: a frame-comparison harness. Render a fixed list of scenes —
`example_scenes.py` plus a selection from the `videos` repo covering 2D fill, stroke joints,
3D surfaces, text, and images — at a fixed resolution with `-s`, and compare against
GL-rendered references with a perceptual tolerance. Exact equality will not hold (different
rasterizer, different depth precision), so the tolerance and a visible diff image matter more
than a pass/fail bit.

This is not optional. It is the only way to know that a thousand small shader edits did not
quietly break the stroke joints on one kind of corner.

### Phase 4 — what the framework then makes easy

Only after parity. These are the reasons to want wgpu rather than merely to tolerate it.

- **Compute-shader curve subdivision.** The stroke shader currently emits
  `6 × (32 - 1) = 186` vertices per curve unconditionally and collapses the unused ones to a
  point — a curve needing three segments still pays for thirty-one. A compute pre-pass
  writing exactly the geometry each curve needs would cut vertex work substantially on
  text-heavy scenes, which are most scenes. There is no equivalent under GL, which is why
  the current allowance scheme exists.
- **One uniform buffer with dynamic offsets** instead of a buffer and bind group per
  mobject. Scenes with thousands of mobjects currently pay per-mobject binding cost.
- **Instanced draws** where the `verts_per_record` multiplication is really instancing.

---

## Ledger

**Dependencies:** `moderngl`, `moderngl_window`, `PyOpenGL`, `pyglet`, `screeninfo` →
`wgpu`, `glfw`. Five to two.

**Code:** roughly flat in total line count, but the composition changes substantially.
Deleted, approximately: 110 lines of uniform-mirroring in `utils/shaders.py`, 50 lines of
uniform-block introspection, 30 lines of raw-GL depth-stencil attachment, the framebuffer
blit chain and its multisample workaround, 40 lines of imperative stencil state, the
buffer-as-texture aliasing and its sampler workaround, and ~90 lines of
`moderngl_window` ceremony and window hacks. Added: a pipeline cache and state table
(~200 lines), a present pipeline (~15 lines of WGSL), and a padded readback (~10 lines).

The honest summary is not "less code" but "the same amount of code, with ~350 lines of
workaround, driver-bug shim, and framework ceremony replaced by ~230 lines of declarative
setup." Every deleted comment explaining why GL made something awkward is a win that does
not show up in a line count.

## Risks

- **wgpu-py maturity.** Pre-1.0, with API renames between versions. Pin it, and expect to
  read wgpu-native's validation errors rather than friendly Python ones. Losing moderngl's
  error messages is a real cost during the port.
- **MSAA with stencil-then-cover.** Untested combination here; 2D scenes use `samples=0`
  because the winding fill plus border stroke already anti-aliases, but `ThreeDCamera`
  defaults to `samples=4`. Verify in the Phase 1 spike.
- **Per-mobject bind group cost.** wgpu makes explicit what moderngl did implicitly, so bind
  groups must be cached on the wrapper and rebuilt only when the underlying buffer is
  replaced — which is exactly where `init_data_texture` is called today, so the hook exists.
- **Depth remap and stroke joints** are the two places where "looks nearly right" is the
  dangerous failure mode. Both are covered by Phase 3 or they are not covered at all.
- **`--autoreload` and `scene.reload()`.** A new `Camera` is built against an existing
  window. Under wgpu the device and surface persist and only the render target is recreated,
  which is simpler than today's `detect_framebuffer(0)` workaround — but worth an explicit
  test, since reload is the single most-used development path.

## On "manim in the web"

Worth being precise about what this does and does not buy. It does not make the Python
codebase run in a browser. What it does is make the GPU-facing half of manim a portable
artifact: the `.wgsl` sources, the buffer layouts, and the pipeline state table are all
things a JS or Rust-wasm front end can consume unchanged. A web renderer would still be a
separate front end, but it would share the shaders and the data layouts rather than
reimplementing them.

The only thing needed now to keep that door open costs nothing: keep the shader sources free
of Python-side codegen beyond the `DATA_LAYOUT` block, and make the layout description
(dtypes, offsets, uniform block members) serializable rather than implicit. That is already
nearly true after #2482.
