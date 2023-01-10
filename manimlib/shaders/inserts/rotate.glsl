mat3 rotationMatrix(vec3 axis, float angle) {
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;
    float ax = axis.x;
    float ay = axis.y;
    float az = axis.z;
    
    return mat3(
        oc * ax * ax + c,      oc * ax * ay - az * s, oc * az * ax + ay * s,
        oc * ax * ay + az * s, oc * ay * ay + c,      oc * ay * az - ax * s,
        oc * az * ax - ay * s, oc * ay * az + ax * s, oc * az * az + c
    );
}

vec3 rotate(vec3 vect, float angle, vec3 axis){
    return rotationMatrix(axis, angle) * vect;
}
