// A sigma.js node program that draws each note as a softly lit sphere with a halo of its own colour, in the
// spirit of Obsidian's and Baalda's graphs. Same data as sigma's circle program; only the shaders differ.
// The halo is drawn inside a larger triangle (HALO times the radius) and never counts for clicks.
import { NodeCircleProgram } from "sigma/rendering";

const HALO = 2.6;

const VERTEX = /* glsl */ `
attribute vec4 a_id;
attribute vec4 a_color;
attribute vec2 a_position;
attribute float a_size;
attribute float a_angle;

uniform mat3 u_matrix;
uniform float u_sizeRatio;
uniform float u_correctionRatio;

varying vec4 v_color;
varying vec2 v_diffVector;
varying float v_radius;

const float bias = 255.0 / 254.0;

void main() {
  float size = a_size * u_correctionRatio / u_sizeRatio * 4.0;
  #ifdef PICKING_MODE
  float reach = 1.0;
  #else
  float reach = ${HALO.toFixed(2)};
  #endif
  vec2 diffVector = size * reach * vec2(cos(a_angle), sin(a_angle));
  gl_Position = vec4((u_matrix * vec3(a_position + diffVector, 1)).xy, 0, 1);
  v_diffVector = diffVector;
  v_radius = size / 2.0;
  #ifdef PICKING_MODE
  v_color = a_id;
  #else
  v_color = a_color;
  #endif
  v_color.a *= bias;
}
`;

const FRAGMENT = /* glsl */ `
precision highp float;

varying vec4 v_color;
varying vec2 v_diffVector;
varying float v_radius;

uniform float u_correctionRatio;

void main(void) {
  float d = length(v_diffVector) / v_radius;          // 0 at the centre, 1 at the sphere's edge
  #ifdef PICKING_MODE
  gl_FragColor = d <= 1.0 ? v_color : vec4(0.0);
  #else
  float aa = u_correctionRatio * 2.0 / v_radius;       // one pixel or so, for a soft edge
  vec3 base = v_color.rgb;
  // the lit sphere: light from the top left, a little rim light, a small highlight
  vec2 p = v_diffVector / v_radius;
  float z = sqrt(max(0.0, 1.0 - min(d * d, 1.0)));
  vec3 n = vec3(p.x, p.y, z);
  float diffuse = clamp(dot(n, normalize(vec3(-0.45, 0.55, 0.75))), 0.0, 1.0);
  float spec = pow(clamp(dot(n, normalize(vec3(-0.3, 0.45, 0.85))), 0.0, 1.0), 24.0);
  vec3 lit = base * (0.42 + 0.68 * diffuse) + vec3(spec * 0.35) + base * pow(1.0 - z, 3.0) * 0.35;
  float core = 1.0 - smoothstep(1.0 - aa, 1.0, d);
  // the halo: the node's colour fading out around it
  float halo = (1.0 - core) * exp(-(d - 1.0) * 2.8) * 0.2 * smoothstep(${HALO.toFixed(2)}, ${(HALO * 0.7).toFixed(2)}, d);
  float a = v_color.a;
  gl_FragColor = vec4(lit * core * a + base * halo * a, (core + halo) * a);
  #endif
}
`;

export class NodeGlowProgram extends NodeCircleProgram {
  getDefinition() {
    return { ...super.getDefinition(), VERTEX_SHADER_SOURCE: VERTEX, FRAGMENT_SHADER_SOURCE: FRAGMENT };
  }
}
