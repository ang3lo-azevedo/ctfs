#version 450

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inNormal;

layout(set = 0, binding = 0) uniform Uniforms {
    mat4 modelMatrix;
    mat4 modelViewProjMatrix;
    mat4 normalMatrix;
    vec4 cameraPosition;
} uniforms;

layout(location = 0) out vec3 fragNormal;
layout(location = 1) out vec3 fragPosition;

void main() {
    gl_Position = uniforms.modelViewProjMatrix * vec4(inPosition, 1.0);
    fragPosition = (uniforms.modelMatrix * vec4(inPosition, 1.0)).xyz;
    fragNormal = normalize(mat3(uniforms.normalMatrix) * inNormal);
}