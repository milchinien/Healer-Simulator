shader_type canvas_item;
render_mode unshaded;

// Shared material ramps: fixed 64-color environment palette, no smooth shading.
const vec3 PALETTE[64] = vec3[64](
	vec3(0.06275, 0.08235, 0.18039),
	vec3(0.09412, 0.11373, 0.25882),
	vec3(0.14118, 0.15294, 0.31765),
	vec3(0.19608, 0.19608, 0.39216),
	vec3(0.26667, 0.25098, 0.45882),
	vec3(0.34510, 0.30196, 0.52941),
	vec3(0.44706, 0.34902, 0.54902),
	vec3(0.57647, 0.39608, 0.56863),
	vec3(0.71765, 0.46667, 0.56863),
	vec3(0.84706, 0.54510, 0.60392),
	vec3(0.93333, 0.62745, 0.55686),
	vec3(1.00000, 0.75686, 0.55686),
	vec3(1.00000, 0.94118, 0.69020),
	vec3(1.00000, 0.82353, 0.43137),
	vec3(0.93333, 0.63922, 0.27059),
	vec3(0.74118, 0.43922, 0.23137),
	vec3(0.50980, 0.26275, 0.18431),
	vec3(0.31765, 0.18039, 0.19216),
	vec3(0.17255, 0.13333, 0.18039),
	vec3(0.23137, 0.16863, 0.22745),
	vec3(0.31765, 0.20784, 0.26667),
	vec3(0.41176, 0.25882, 0.32157),
	vec3(0.52157, 0.31765, 0.39608),
	vec3(0.63922, 0.40000, 0.46275),
	vec3(0.76863, 0.50196, 0.51373),
	vec3(0.20000, 0.20000, 0.29804),
	vec3(0.28235, 0.26667, 0.36471),
	vec3(0.37647, 0.33725, 0.43137),
	vec3(0.47451, 0.40392, 0.49020),
	vec3(0.57255, 0.48627, 0.54902),
	vec3(0.70196, 0.60784, 0.62353),
	vec3(0.82353, 0.70980, 0.67451),
	vec3(0.12549, 0.15294, 0.26667),
	vec3(0.18824, 0.24314, 0.39608),
	vec3(0.27059, 0.32157, 0.48627),
	vec3(0.37647, 0.40784, 0.54902),
	vec3(0.48627, 0.50196, 0.63529),
	vec3(0.14510, 0.17647, 0.21176),
	vec3(0.20784, 0.28235, 0.22353),
	vec3(0.32549, 0.38824, 0.28235),
	vec3(0.49412, 0.50196, 0.31373),
	vec3(0.68627, 0.63922, 0.39608),
	vec3(0.40000, 0.23137, 0.27843),
	vec3(0.56863, 0.27451, 0.31373),
	vec3(0.71373, 0.36471, 0.37647),
	vec3(0.84314, 0.47451, 0.44706),
	vec3(0.42353, 0.32549, 0.29412),
	vec3(0.59608, 0.45882, 0.35686),
	vec3(0.09020, 0.16863, 0.21176),
	vec3(0.14118, 0.30196, 0.31373),
	vec3(0.22353, 0.44314, 0.44706),
	vec3(0.34902, 0.57647, 0.54118),
	vec3(0.54510, 0.71765, 0.64314),
	vec3(0.21569, 0.32941, 0.21569),
	vec3(0.32157, 0.45098, 0.25882),
	vec3(0.45490, 0.58824, 0.32941),
	vec3(0.63137, 0.69412, 0.42745),
	vec3(0.79608, 0.82353, 0.60784),
	vec3(0.42353, 0.58039, 0.68627),
	vec3(0.58824, 0.70588, 0.79608),
	vec3(0.75294, 0.79608, 0.83137),
	vec3(0.88627, 0.83922, 0.74118),
	vec3(0.91373, 0.47843, 0.20392),
	vec3(0.98431, 0.72157, 0.32941)
);

vec3 palette_color(vec3 color) {
	float best_distance = 10.0;
	vec3 best = PALETTE[0];
	for (int i = 0; i < 64; i++) {
		vec3 delta = color - PALETTE[i];
		float distance = dot(delta, delta);
		if (distance < best_distance) {
			best_distance = distance;
			best = PALETTE[i];
		}
	}
	return best;
}

uniform vec4 motion_a = vec4(0.0);
uniform vec4 motion_b = vec4(0.0);
uniform vec4 water_region = vec4(0.0);
uniform float motion_strength = 1.0;
// Rotating inner mechanisms: center/radius in 640x360 coordinates, angular speed.
uniform vec4 gear_a = vec4(0.0);
uniform vec4 gear_b = vec4(0.0);

vec2 mechanism_uv(vec2 uv, vec4 gear) {
	vec2 offset = uv * vec2(640.0, 360.0) - gear.xy;
	if (gear.z > 0.0 && length(offset) < gear.z) {
		float angle = floor(TIME * 6.0) / 6.0 * gear.w;
		mat2 rotation = mat2(vec2(cos(angle), sin(angle)), vec2(-sin(angle), cos(angle)));
		vec2 pixel = gear.xy + rotation * offset;
		return (floor(pixel / 2.0) * 2.0 + 1.0) / vec2(640.0, 360.0);
	}
	return uv;
}

// Local sky layers: keep architecture, mountain, moon and plaza fixed.
// Rectangles are in the source art's normalized coordinates, entirely in sky.
float sky_region(vec2 uv, vec4 bounds) {
	if (bounds.z <= bounds.x || bounds.w <= bounds.y) { return 0.0; }
	vec2 fade_in = smoothstep(bounds.xy, bounds.xy + vec2(0.022), uv);
	vec2 fade_out = 1.0 - smoothstep(bounds.zw - vec2(0.022), bounds.zw, uv);
	return fade_in.x * fade_in.y * fade_out.x * fade_out.y;
}

void fragment() {
	vec2 uv = UV;
	uv = mechanism_uv(uv, gear_a);
	uv = mechanism_uv(uv, gear_b);
	float far_clouds = sky_region(uv, motion_a);
	float near_clouds = sky_region(uv, motion_b);
	// Slow breathing/drifting, quantized to game pixels; never blur the dithering.
	float drift = far_clouds * sin(TIME * 0.095) * 3.0;
	drift += near_clouds * sin(TIME * 0.13 + 0.7) * 2.0;
	uv.x += floor(drift * motion_strength * 0.5 + 0.5) / 320.0;
	vec4 source = texture(TEXTURE, uv);
	vec3 mapped = palette_color(source.rgb);
	// Quantized travelling highlights only on blue water, never on the banks.
	float water = sky_region(UV, water_region);
	if (water > 0.2 && source.b > source.r * 1.18 && source.b > source.g * 0.95) {
		float ripple = sin(floor(UV.y * 180.0) * 1.8 + floor(TIME * 4.0));
		if (ripple > 0.86) { mapped = palette_color(source.rgb + vec3(0.08)); }
	}
	COLOR = vec4(mapped, source.a);
}
