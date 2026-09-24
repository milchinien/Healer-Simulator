shader_type canvas_item;
render_mode unshaded;

// Shared material ramps: fixed 48-color environment palette, no smooth shading.
const vec3 PALETTE[48] = vec3[48](
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
	vec3(0.59608, 0.45882, 0.35686)
);

vec3 palette_color(vec3 color) {
	float best_distance = 10.0;
	vec3 best = PALETTE[0];
	for (int i = 0; i < 48; i++) {
		vec3 delta = color - PALETTE[i];
		float distance = dot(delta, delta);
		if (distance < best_distance) {
			best_distance = distance;
			best = PALETTE[i];
		}
	}
	return best;
}

// Local sky layers: keep architecture, mountain, moon and plaza fixed.
// Rectangles are in the source art's normalized coordinates, entirely in sky.
float sky_region(vec2 uv, vec4 bounds) {
	vec2 fade_in = smoothstep(bounds.xy, bounds.xy + vec2(0.022), uv);
	vec2 fade_out = 1.0 - smoothstep(bounds.zw - vec2(0.022), bounds.zw, uv);
	return fade_in.x * fade_in.y * fade_out.x * fade_out.y;
}

void fragment() {
	vec2 uv = UV;
	float far_clouds = sky_region(uv, vec4(0.12, 0.205, 0.505, 0.355));
	float near_clouds = sky_region(uv, vec4(0.70, 0.225, 0.885, 0.335));
	// Slow breathing/drifting, quantized to game pixels; never blur the dithering.
	float drift = far_clouds * sin(TIME * 0.095) * 3.0;
	drift += near_clouds * sin(TIME * 0.13 + 0.7) * 2.0;
	uv.x += floor(drift * 0.5 + 0.5) / 320.0;
	vec4 source = texture(TEXTURE, uv);
	COLOR = vec4(palette_color(source.rgb), source.a);
}
