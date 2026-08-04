/*
Shaders are handed no vertex attributes. Each expands every record of its buffer into
several vertices, and reads the fields it wants out of that buffer itself, using the index
of the vertex being drawn to work out which record it belongs to.

The line below is replaced by constants generated from the mobject's data dtype, giving
DATA_STRIDE along with a DATA_OFFSET_<name> for each field, both counted in floats.
*/
// DATA_LAYOUT

@group(2) @binding(0) var<storage, read> data: array<f32>;

fn read_float(record: u32, offset: u32) -> f32 {
    return data[DATA_STRIDE * record + offset];
}

fn read_vec2(record: u32, offset: u32) -> vec2f {
    return vec2f(read_float(record, offset), read_float(record, offset + 1u));
}

fn read_vec3(record: u32, offset: u32) -> vec3f {
    return vec3f(
        read_float(record, offset),
        read_float(record, offset + 1u),
        read_float(record, offset + 2u),
    );
}

fn read_vec4(record: u32, offset: u32) -> vec4f {
    return vec4f(read_vec3(record, offset), read_float(record, offset + 3u));
}
