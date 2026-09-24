// Figuren-Shader: Palettentausch fuer Haut/Haare, Geist-Effekt (gefallene Hardcore-Charaktere)
// und kurzes Aufblitzen bei Aenderungen.
// Index-Ebenen speichern die Farbstufe im Rotkanal: 0 = Kontur, 1 = Schatten, 2 = Basis, 3 = Licht.
shader_type canvas_item;
render_mode unshaded;

uniform bool swap = false;
uniform vec4 c0 : source_color = vec4(0.106, 0.078, 0.141, 1.0);
uniform vec4 c1 : source_color = vec4(0.4, 0.4, 0.4, 1.0);
uniform vec4 c2 : source_color = vec4(0.6, 0.6, 0.6, 1.0);
uniform vec4 c3 : source_color = vec4(0.8, 0.8, 0.8, 1.0);
uniform float ghost : hint_range(0.0, 1.0) = 0.0;
uniform float flash : hint_range(0.0, 1.0) = 0.0;

varying vec4 modulate;

void vertex() {
	modulate = COLOR;
}

void fragment() {
	vec4 t = texture(TEXTURE, UV);
	vec3 col = t.rgb;
	if (swap) {
		float i = floor(t.r * 3.0 + 0.5);
		col = i < 0.5 ? c0.rgb : (i < 1.5 ? c1.rgb : (i < 2.5 ? c2.rgb : c3.rgb));
	}
	if (ghost > 0.0) {
		float g = dot(col, vec3(0.299, 0.587, 0.114));
		vec3 spirit = vec3(g * 0.55 + 0.18, g * 0.7 + 0.28, g * 0.8 + 0.42);
		col = mix(col, spirit, ghost);
	}
	col = mix(col, vec3(1.0, 0.97, 0.85), flash);
	COLOR = vec4(col, t.a * (1.0 - ghost * 0.3)) * modulate;
}
