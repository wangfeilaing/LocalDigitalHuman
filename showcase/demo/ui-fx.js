/* UI-FX: react-bits 动效的原生移植（2026-08-14）
 * 无第三方依赖。包含：
 * 1. Spotlight Card：把鼠标在 .fluent-card 内的坐标写进 CSS 变量 --mx/--my
 * 2. 面板入场：监听 .workbench-panel 的 is-active 变化，给卡片重放错落入场动画
 * 3. Specular Button：主按钮镜面高光描边指向鼠标
 * 4. LightRays：全页 WebGL 光束背景（react-bits LightRays 的原生 WebGL 移植，不用 OGL）
 * 系统开启“减弱动态效果”时自动全部禁用。
 */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* —— Spotlight Card —— */
  function initCardSpotlight() {
    document.addEventListener('pointermove', function (e) {
      var target = e.target;
      if (!target || !target.closest) return;
      var card = target.closest('.fluent-card');
      if (!card) return;
      var rect = card.getBoundingClientRect();
      card.style.setProperty('--mx', (e.clientX - rect.left) + 'px');
      card.style.setProperty('--my', (e.clientY - rect.top) + 'px');
    }, { passive: true });
  }

  /* —— 面板切换错落入场 —— */
  function replayCards(panel) {
    if (reduceMotion || !panel) return;
    var cards = panel.querySelectorAll('.fluent-card');
    cards.forEach(function (card, i) {
      card.classList.remove('ui-fx-enter');
      card.style.animationDelay = (i * 45) + 'ms';
    });
    // 强制 reflow，让移除 class 生效后再重新添加，动画才能重放
    void panel.offsetWidth;
    cards.forEach(function (card) { card.classList.add('ui-fx-enter'); });
  }

  function initPanelReveal() {
    var panels = document.querySelectorAll('.workbench-panel');
    if (!panels.length) return;
    var observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        if (m.type === 'attributes' && m.target.classList.contains('is-active')) {
          replayCards(m.target);
        }
      });
    });
    panels.forEach(function (p) {
      observer.observe(p, { attributes: true, attributeFilter: ['class'] });
    });
    replayCards(document.querySelector('.workbench-panel.is-active'));
  }

  /* —— Specular Button：高光描边指向鼠标（react-bits SpecularButton 移植） —— */
  function initSpecularButtons() {
    var PROXIMITY = 250;
    var SHINE_HALF = 9; // 高光段 18deg 的一半，使高光中心对准鼠标方向

    function distanceToRect(x, y, rect) {
      var dx = Math.max(rect.left - x, 0, x - rect.right);
      var dy = Math.max(rect.top - y, 0, y - rect.bottom);
      return Math.sqrt(dx * dx + dy * dy);
    }

    document.addEventListener('pointermove', function (e) {
      var buttons = document.querySelectorAll('.primary-button');
      buttons.forEach(function (btn) {
        if (btn.disabled) { btn.style.setProperty('--spec-opacity', 0); return; }
        var rect = btn.getBoundingClientRect();
        var dist = distanceToRect(e.clientX, e.clientY, rect);
        if (dist > PROXIMITY) { btn.style.setProperty('--spec-opacity', 0); return; }
        // 从按钮中心指向鼠标的角度（conic-gradient 的 0deg 在正上方，顺时针）
        var cx = rect.left + rect.width / 2;
        var cy = rect.top + rect.height / 2;
        var deg = Math.atan2(e.clientX - cx, -(e.clientY - cy)) * 180 / Math.PI;
        btn.style.setProperty('--spec-angle', (deg - SHINE_HALF) + 'deg');
        btn.style.setProperty('--spec-opacity', (0.9 * (1 - dist / PROXIMITY)).toFixed(3));
      });
    }, { passive: true });

    document.addEventListener('pointerleave', function () {
      document.querySelectorAll('.primary-button').forEach(function (btn) {
        btn.style.setProperty('--spec-opacity', 0);
      });
    });
  }

  /* —— LightRays：WebGL 光束背景（react-bits LightRays 原生移植，不用 OGL） —— */
  function initLightRays() {
    var canvas = document.createElement('canvas');
    canvas.className = 'light-rays-bg';
    canvas.setAttribute('aria-hidden', 'true');
    document.body.insertBefore(canvas, document.body.firstChild);

    var gl = canvas.getContext('webgl', {
      alpha: true, antialias: false, depth: false, stencil: false,
      premultipliedAlpha: false, preserveDrawingBuffer: true
    });
    if (!gl) { canvas.remove(); return; }

    var VERT = [
      'attribute vec2 position;',
      'varying vec2 vUv;',
      'void main() {',
      '  vUv = position * 0.5 + 0.5;',
      '  gl_Position = vec4(position, 0.0, 1.0);',
      '}'
    ].join('\n');

    // 片元着色器逐行来自 react-bits LightRays（参数：top-center / #00ffff / speed 1.5 /
    // spread 0.8 / length 1.2 / mouseInfluence 0.1 / noise 0.1 / distortion 0.05）
    var FRAG = [
      'precision highp float;',
      'uniform float iTime;',
      'uniform vec2  iResolution;',
      'uniform vec2  rayPos;',
      'uniform vec2  rayDir;',
      'uniform vec3  raysColor;',
      'uniform float raysSpeed;',
      'uniform float lightSpread;',
      'uniform float rayLength;',
      'uniform float pulsating;',
      'uniform float fadeDistance;',
      'uniform float saturation;',
      'uniform vec2  mousePos;',
      'uniform float mouseInfluence;',
      'uniform float noiseAmount;',
      'uniform float distortion;',
      'varying vec2 vUv;',
      'float noise(vec2 st) {',
      '  return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);',
      '}',
      'float rayStrength(vec2 raySource, vec2 rayRefDirection, vec2 coord,',
      '                  float seedA, float seedB, float speed) {',
      '  vec2 sourceToCoord = coord - raySource;',
      '  vec2 dirNorm = normalize(sourceToCoord);',
      '  float cosAngle = dot(dirNorm, rayRefDirection);',
      '  float distortedAngle = cosAngle + distortion * sin(iTime * 2.0 + length(sourceToCoord) * 0.01) * 0.2;',
      '  float spreadFactor = pow(max(distortedAngle, 0.0), 1.0 / max(lightSpread, 0.001));',
      '  float distance = length(sourceToCoord);',
      '  float maxDistance = iResolution.x * rayLength;',
      '  float lengthFalloff = clamp((maxDistance - distance) / maxDistance, 0.0, 1.0);',
      '  float fadeFalloff = clamp((iResolution.x * fadeDistance - distance) / (iResolution.x * fadeDistance), 0.5, 1.0);',
      '  float pulse = pulsating > 0.5 ? (0.8 + 0.2 * sin(iTime * speed * 3.0)) : 1.0;',
      '  float baseStrength = clamp(',
      '    (0.45 + 0.15 * sin(distortedAngle * seedA + iTime * speed)) +',
      '    (0.3 + 0.2 * cos(-distortedAngle * seedB + iTime * speed)),',
      '    0.0, 1.0',
      '  );',
      '  return baseStrength * lengthFalloff * fadeFalloff * spreadFactor * pulse;',
      '}',
      'void mainImage(out vec4 fragColor, in vec2 fragCoord) {',
      '  vec2 coord = vec2(fragCoord.x, iResolution.y - fragCoord.y);',
      '  vec2 finalRayDir = rayDir;',
      '  if (mouseInfluence > 0.0) {',
      '    vec2 mouseScreenPos = mousePos * iResolution.xy;',
      '    vec2 mouseDirection = normalize(mouseScreenPos - rayPos);',
      '    finalRayDir = normalize(mix(rayDir, mouseDirection, mouseInfluence));',
      '  }',
      '  vec4 rays1 = vec4(1.0) * rayStrength(rayPos, finalRayDir, coord, 36.2214, 21.11349, 1.5 * raysSpeed);',
      '  vec4 rays2 = vec4(1.0) * rayStrength(rayPos, finalRayDir, coord, 22.3991, 18.0234, 1.1 * raysSpeed);',
      '  fragColor = rays1 * 0.5 + rays2 * 0.4;',
      '  if (noiseAmount > 0.0) {',
      '    float n = noise(coord * 0.01 + iTime * 0.1);',
      '    fragColor.rgb *= (1.0 - noiseAmount + noiseAmount * n);',
      '  }',
      '  float brightness = 1.0 - (coord.y / iResolution.y);',
      '  fragColor.x *= 0.1 + brightness * 0.8;',
      '  fragColor.y *= 0.3 + brightness * 0.6;',
      '  fragColor.z *= 0.5 + brightness * 0.5;',
      '  if (saturation != 1.0) {',
      '    float gray = dot(fragColor.rgb, vec3(0.299, 0.587, 0.114));',
      '    fragColor.rgb = mix(vec3(gray), fragColor.rgb, saturation);',
      '  }',
      '  fragColor.rgb *= raysColor;',
      '  fragColor.rgb *= 1.8;',   // 提亮：默认强度在全屏深色背景上太弱
      '}',
      'void main() {',
      '  vec4 color;',
      '  mainImage(color, gl_FragCoord.xy);',
      '  gl_FragColor = color;',
      '}'
    ].join('\n');

    function compile(type, src) {
      var shader = gl.createShader(type);
      gl.shaderSource(shader, src);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.warn('LightRays shader error:', gl.getShaderInfoLog(shader));
        return null;
      }
      return shader;
    }

    var vs = compile(gl.VERTEX_SHADER, VERT);
    var fs = compile(gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) { canvas.remove(); return; }

    var program = gl.createProgram();
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.warn('LightRays link error:', gl.getProgramInfoLog(program));
      canvas.remove();
      return;
    }
    gl.useProgram(program);

    // 全屏大三角（OGL Triangle 等价）
    var buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var posLoc = gl.getAttribLocation(program, 'position');
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    gl.enable(gl.BLEND);
    // 光束用纯加法混合（暗色背景上"发光"而不是"半透明叠加"），否则白色光束在深底上几乎看不见
    gl.blendFunc(gl.ONE, gl.ONE);
    gl.clearColor(0, 0, 0, 0);

    var U = {};
    ['iTime', 'iResolution', 'rayPos', 'rayDir', 'raysColor', 'raysSpeed', 'lightSpread',
      'rayLength', 'pulsating', 'fadeDistance', 'saturation', 'mousePos', 'mouseInfluence',
      'noiseAmount', 'distortion'].forEach(function (name) {
      U[name] = gl.getUniformLocation(program, name);
    });

    // 参数：top-center / #ffffff（配合深色背景的白色光晕） / 1.5 / 0.8 / 1.2 / followMouse / 0.1 / 0.1 / 0.05
    gl.uniform3f(U.raysColor, 1.0, 1.0, 1.0);   // #ffffff
    gl.uniform1f(U.raysSpeed, 1.5);
    gl.uniform1f(U.lightSpread, 0.8);
    gl.uniform1f(U.rayLength, 1.2);
    gl.uniform1f(U.pulsating, 0.0);
    gl.uniform1f(U.fadeDistance, 1.0);
    gl.uniform1f(U.saturation, 1.0);
    gl.uniform1f(U.mouseInfluence, 0.1);
    gl.uniform1f(U.noiseAmount, 0.1);
    gl.uniform1f(U.distortion, 0.05);

    var mouse = { x: 0.5, y: 0.5 };
    var smoothMouse = { x: 0.5, y: 0.5 };

    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w = Math.floor(window.innerWidth * dpr);
      var h = Math.floor(window.innerHeight * dpr);
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
        gl.viewport(0, 0, w, h);
      }
      gl.uniform2f(U.iResolution, w, h);
      // raysOrigin: top-center
      gl.uniform2f(U.rayPos, 0.5 * w, -0.2 * h);
      gl.uniform2f(U.rayDir, 0, 1);
    }
    window.addEventListener('resize', resize);
    resize();

    window.addEventListener('mousemove', function (e) {
      mouse.x = e.clientX / window.innerWidth;
      mouse.y = e.clientY / window.innerHeight;
    }, { passive: true });

    var startTime = performance.now();
    function frame(now) {
      gl.uniform1f(U.iTime, (now - startTime) * 0.001);
      var s = 0.92;
      smoothMouse.x = smoothMouse.x * s + mouse.x * (1 - s);
      smoothMouse.y = smoothMouse.y * s + mouse.y * (1 - s);
      gl.uniform2f(U.mousePos, smoothMouse.x, smoothMouse.y);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      requestAnimationFrame(frame);
    }

    if (reduceMotion) {
      // 减弱动态：只渲染一帧静态光束
      gl.uniform1f(U.iTime, 0);
      gl.uniform2f(U.mousePos, 0.5, 0.5);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    } else {
      requestAnimationFrame(frame);
    }
  }

  function init() {
    initCardSpotlight();
    initPanelReveal();
    initSpecularButtons();
    initLightRays();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
