/*
Shaders which expand each vertex record into several vertices, rather than
relying on a geometry shader to do that, are handed no vertex attributes at all.
Instead they index into the vertex buffer themselves, using gl_VertexID to work
out which record they want, and these functions to read fields out of it.

The line below is replaced by ShaderWrapper with constants generated from the
mobject's data dtype, giving DATA_STRIDE along with a DATA_OFFSET_<name> for
each field, both measured in floats.
*/
// DATA_LAYOUT

uniform samplerBuffer Data;

float read_float(int record, int offset){
    return texelFetch(Data, DATA_STRIDE * record + offset).r;
}

vec2 read_vec2(int record, int offset){
    return vec2(
        read_float(record, offset + 0),
        read_float(record, offset + 1)
    );
}

vec3 read_vec3(int record, int offset){
    return vec3(
        read_float(record, offset + 0),
        read_float(record, offset + 1),
        read_float(record, offset + 2)
    );
}

vec4 read_vec4(int record, int offset){
    return vec4(read_vec3(record, offset), read_float(record, offset + 3));
}
