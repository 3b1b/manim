
vec3 get_unit_normal(in vec3 point0, in vec3 point1, in vec3 point2){
    vec3 cp = cross(point1 - point0, point2 - point1);
    if(length(cp) == 0){
        return vec3(0.0, 0.0, 1.0);
    }else{
        if(cp.z < 0){
            // After re-orienting, camera will always sit in the positive
            // z-direction.  We always want normal vectors pointing towards
            // the camera.
            cp *= -1;
        }
        return normalize(cp);
    }
}