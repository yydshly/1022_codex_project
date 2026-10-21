// WebGL 2 adapter for the MIT-licensed SwiftUIShaders algorithms.
const VERTEX = `#version 300 es
void main() {
    vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2));
    gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}`;

export class ShaderRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.gl = canvas.getContext('webgl2', { alpha: false, antialias: false, preserveDrawingBuffer: true });
    if (!this.gl) throw new Error('浏览器未能启用 WebGL 2。请在支持 WebGL 2 的浏览器中开启硬件加速后重试。');
    const gl = this.gl;
    this.programs = new Map();
    this.vertex = this.compile(gl.VERTEX_SHADER, VERTEX);
    this.vao = gl.createVertexArray();
    gl.bindVertexArray(this.vao);
    this.texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.clearColor(0.06, 0.08, 0.07, 1);
  }

  compile(type, source) {
    const gl = this.gl;
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const error = gl.getShaderInfoLog(shader);
      gl.deleteShader(shader);
      throw new Error(error);
    }
    return shader;
  }

  program(effect) {
    if (this.programs.has(effect.id)) return this.programs.get(effect.id);
    const gl = this.gl;
    const fragment = this.compile(gl.FRAGMENT_SHADER, effect.fragment);
    const program = gl.createProgram();
    gl.attachShader(program, this.vertex);
    gl.attachShader(program, fragment);
    gl.linkProgram(program);
    gl.deleteShader(fragment);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      const error = gl.getProgramInfoLog(program);
      gl.deleteProgram(program);
      throw new Error(error);
    }
    const uniforms = {};
    for (const name of ['uSize', 'uResolution', 'uTime', 'uParams[0]', 'uTouch', 'uCompare', 'uImage']) {
      uniforms[name] = gl.getUniformLocation(program, name);
    }
    let paramCount = 0;
    for (let i = 0; i < gl.getProgramParameter(program, gl.ACTIVE_UNIFORMS); i++) {
      const info = gl.getActiveUniform(program, i);
      if (info.name === 'uParams[0]') paramCount = info.size;
    }
    const result = { program, uniforms, paramCount };
    this.programs.set(effect.id, result);
    return result;
  }

  setImage(image) {
    const gl = this.gl;
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.texture);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
  }

  draw(effect, values, { width = 450, height = 600, time = 1.7, touch = [0.5, 0.5], compare = -1, scale = 1 } = {}) {
    const gl = this.gl;
    const entry = this.program(effect);
    const w = Math.max(1, Math.round(width * scale));
    const h = Math.max(1, Math.round(height * scale));
    if (this.canvas.width !== w || this.canvas.height !== h) {
      this.canvas.width = w;
      this.canvas.height = h;
    }
    gl.viewport(0, 0, w, h);
    gl.useProgram(entry.program);
    gl.bindVertexArray(this.vao);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.texture);
    const u = entry.uniforms;
    // A common 450×600 user-space layer makes pixel-distance effects comparable
    // across screen sizes; canvas resolution is independent of effect geometry.
    gl.uniform2f(u.uSize, 450, 600);
    gl.uniform2f(u.uResolution, w, h);
    gl.uniform1f(u.uTime, time);
    gl.uniform2f(u.uTouch, touch[0], touch[1]);
    gl.uniform1f(u.uCompare, compare);
    gl.uniform1i(u.uImage, 0);
    const params = effect.params.map(p => p.type === 'point' ? 0 : values[p.label] ?? p.default);
    if (entry.paramCount) gl.uniform1fv(u['uParams[0]'], params.slice(0, entry.paramCount));
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  dispose() {
    const gl = this.gl;
    for (const entry of this.programs.values()) gl.deleteProgram(entry.program);
    gl.deleteShader(this.vertex);
    gl.deleteTexture(this.texture);
    gl.deleteVertexArray(this.vao);
  }
}
