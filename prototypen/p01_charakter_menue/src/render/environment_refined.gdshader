shader_type canvas_item;
render_mode unshaded;

// Preserve authored colors; no nearest-palette quantization in the refined edition.
vec3 palette_color(vec3 color) { return color; }

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
		return (floor(pixel) + 0.5) / vec2(640.0, 360.0);
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
	uv.x += floor(drift * motion_strength + 0.5) / 640.0;
	vec4 source = texture(TEXTURE, uv);
	vec3 mapped = palette_color(source.rgb);
	// Quantized travelling highlights only on blue water, never on the banks.
	float water = sky_region(UV, water_region);
	if (water > 0.2 && source.b > source.r * 1.18 && source.b > source.g * 0.95) {
		float ripple = sin(floor(UV.y * 360.0) * 1.8 + floor(TIME * 4.0));
		if (ripple > 0.86) { mapped = palette_color(source.rgb + vec3(0.08)); }
	}
	COLOR = vec4(mapped, source.a);
}
