#version 450

layout(location = 0) in vec3 fragNormal;
layout(location = 1) in vec3 fragPosition;

layout(location = 0) out vec4 outColor;

void main() {
    vec3 debugColor = normalize(fragNormal) * 0.5 + 0.5;
    vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
    float diffuse = max(dot(fragNormal, lightDir), 0.2);
    #outColor = vec4(normalize(fragNormal) * 0.5 + 0.5, 1.0);
    outColor = vec4(debugColor, 1.0);
}