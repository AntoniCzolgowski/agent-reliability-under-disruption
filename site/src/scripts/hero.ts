// The breathing city: the 200 x 200 grid as a landscape whose height is how many people are observed
// in each cell, cycling through the 24 hours of a workday. Data comes from public/data/hero.webp
// (exported by code/export_hero.py). Two render styles: ridges (200 ridgelines) and columns (40,000 boxes).
import {
  Scene, PerspectiveCamera, WebGLRenderer, Color, BufferGeometry, BufferAttribute, Mesh, MeshBasicMaterial,
  InstancedBufferGeometry, InstancedBufferAttribute, BoxGeometry, ShaderMaterial, Vector2, DynamicDrawUsage,
} from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";

export interface HeroHeader {
  atlas: string; grid: number; slots: number; frame_columns: number; frame_rows: number; vmax: number;
  slot_totals_ordinary: number[]; slot_totals_emergency: number[];
}

export interface HeroOptions {
  style: "ridges" | "columns";
  dataUrl: string;            // folder with hero.json and the atlas
  autoplay: boolean;          // false under reduced motion
  idleRotation: boolean;      // false under reduced motion
  startSlot: number;          // 8 = 04:00
  onTime: (slot: number) => void;
  onReady: () => void;
  onLost: () => void;
}

export interface HeroHandle {
  play(): void; pause(): void; playing(): boolean;
  seek(slot: number): void; slot(): number;
  setCondition(emergency: boolean): void;
  still(slot: number): string;   // renders one frame at the default view and returns a PNG data URL
  dispose(): void;
}

const COBALT = new Color("#1F4FD8"), VERMILION = new Color("#E8412A"), GROUND = new Color("#FCFCFA");
const HEIGHT = 30;                 // world units for pixel value 255 (grid is 200 units wide)
const SLOTS_PER_SECOND = 2;        // one day in 24 s
const MORPH_MS = 800;
const GHOST_OPACITY = 0.15;
// any azimuth; polar angle from straight above (8 degrees) down to just above the plane (82 degrees), never from below
const POLAR_MIN = (8 * Math.PI) / 180, POLAR_MAX = (82 * Math.PI) / 180, POLAR_DEFAULT = (58 * Math.PI) / 180;
const IDLE_SPEED = 0.011;          // rad/s, continuous slow turn until the first drag
const INTRO_MS = 4600;             // entry move: from far away and behind, half a turn into the default view


async function loadAtlas(dataUrl: string): Promise<{ header: HeroHeader; ord: Uint8Array[]; emg: Uint8Array[] }> {
  const header: HeroHeader = await (await fetch(`${dataUrl}hero.json`)).json();
  const blob = await (await fetch(`${dataUrl}${header.atlas}`)).blob();
  const bitmap = await createImageBitmap(blob, { colorSpaceConversion: "none", premultiplyAlpha: "none" });
  const g = header.grid, w = header.frame_columns * g, h = header.frame_rows * g;
  const cv = document.createElement("canvas"); cv.width = w; cv.height = h;
  const ctx = cv.getContext("2d", { willReadFrequently: true })!;
  ctx.drawImage(bitmap, 0, 0); bitmap.close();
  const px = ctx.getImageData(0, 0, w, h).data;
  const ord: Uint8Array[] = [], emg: Uint8Array[] = [];
  for (let i = 0; i < header.slots; i++) {
    const fx = (i % header.frame_columns) * g, fy = Math.floor(i / header.frame_columns) * g;
    const a = new Uint8Array(g * g), b = new Uint8Array(g * g);
    for (let y = 0; y < g; y++) {
      let src = ((fy + y) * w + fx) * 4, dst = y * g;
      for (let x = 0; x < g; x++, src += 4, dst++) { a[dst] = px[src]; b[dst] = px[src + 1]; }
    }
    ord.push(a); emg.push(b);
  }
  return { header, ord, emg };
}

export async function mountHero(canvas: HTMLCanvasElement, opts: HeroOptions): Promise<HeroHandle> {
  const { header, ord, emg } = await loadAtlas(opts.dataUrl);
  const G = header.grid, N = G * G, SLOTS = header.slots;

  const renderer = new WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  const scene = new Scene();
  const camera = new PerspectiveCamera(34, 1, 1, 2000);

  // heights for the current frame, mixed between conditions during the morph
  const heights = new Float32Array(N);
  const ghost = new Float32Array(N);
  let slot = opts.startSlot, playing = false, emergency = false, mix = 0, mixTarget = 0;
  let azimuth = 0, polar = POLAR_DEFAULT, azVel = 0, polVel = 0, dragged = false, distScale = 1;
  let introStart = -1;
  let needRender = true, raf = 0, lastTs = 0, disposed = false, lost = false;

  function computeHeights() {
    const i0 = Math.floor(slot) % SLOTS, i1 = (i0 + 1) % SLOTS, f = slot - Math.floor(slot);
    const a0 = ord[i0], a1 = ord[i1], b0 = emg[i0], b1 = emg[i1];
    const k = HEIGHT / 255;
    for (let c = 0; c < N; c++) {
      const o = (a0[c] + (a1[c] - a0[c]) * f) * k;
      const e = (b0[c] + (b1[c] - b0[c]) * f) * k;
      ghost[c] = o;
      heights[c] = o + (e - o) * mix;
    }
  }

  // world coordinates: x across, z toward the viewer, y up; cell (x, y) at (x - 99.5, ., y - 99.5)
  const wx = (x: number) => x - (G - 1) / 2, wz = (y: number) => y - (G - 1) / 2;
  // narrow canvases draw every second ridge, otherwise 200 lines merge into a block
  const STRIDE = canvas.clientWidth > 0 && canvas.clientWidth < 700 ? 2 : 1;
  const rowsY: number[] = []; for (let y = 0; y < G; y += STRIDE) rowsY.push(y);
  const R = rowsY.length;

  // ---- style: ridges -------------------------------------------------------------------------
  type Ridges = { line: LineSegments2; ghostLine: LineSegments2; strips: Mesh; linePos: Float32Array; ghostPos: Float32Array; stripPos: Float32Array; lineMat: LineMaterial; ghostMat: LineMaterial };
  let ridges: Ridges | null = null;
  function buildRidges(): Ridges {
    const segs = R * (G - 1);
    const linePos = new Float32Array(segs * 6), ghostPos = new Float32Array(segs * 6);
    let p = 0;
    for (const y of rowsY) for (let x = 0; x < G - 1; x++) {
      linePos[p] = wx(x); linePos[p + 1] = 0; linePos[p + 2] = wz(y);
      linePos[p + 3] = wx(x + 1); linePos[p + 4] = 0; linePos[p + 5] = wz(y);
      p += 6;
    }
    ghostPos.set(linePos);
    const makeLine = (pos: Float32Array, color: Color, opacity: number) => {
      const geo = new LineSegmentsGeometry(); geo.setPositions(pos);
      (geo.attributes.instanceStart as any).data.setUsage(DynamicDrawUsage);
      const mat = new LineMaterial({ color: color.getHex(), linewidth: STRIDE > 1 ? 1.1 : 1.25, transparent: true, opacity, depthWrite: opacity >= 1 });
      mat.resolution = new Vector2(1, 1);
      const line = new LineSegments2(geo, mat); line.frustumCulled = false;
      return { line, mat };
    };
    const a = makeLine(linePos, COBALT, 1), b = makeLine(ghostPos, COBALT, 0);
    b.line.visible = false; b.line.renderOrder = -1;

    // fill strips: for each row a vertical curtain from the ridge down to the ground, in the ground colour
    const stripPos = new Float32Array(R * G * 2 * 3);
    const idx = new Uint32Array(R * (G - 1) * 6);
    let q = 0;
    for (let ri = 0; ri < R; ri++) {
      const y = rowsY[ri];
      for (let x = 0; x < G; x++) {
        const t = (ri * G + x) * 2;
        stripPos[t * 3] = wx(x); stripPos[t * 3 + 1] = 0; stripPos[t * 3 + 2] = wz(y);
        stripPos[t * 3 + 3] = wx(x); stripPos[t * 3 + 4] = -0.5; stripPos[t * 3 + 5] = wz(y);
      }
      for (let x = 0; x < G - 1; x++) {
        const t0 = (ri * G + x) * 2, b0 = t0 + 1, t1 = t0 + 2, b1 = t0 + 3;
        idx[q++] = t0; idx[q++] = b0; idx[q++] = t1; idx[q++] = b0; idx[q++] = b1; idx[q++] = t1;
      }
    }
    const sg = new BufferGeometry();
    const posAttr = new BufferAttribute(stripPos, 3); posAttr.setUsage(DynamicDrawUsage);
    sg.setAttribute("position", posAttr); sg.setIndex(new BufferAttribute(idx, 1));
    const sm = new MeshBasicMaterial({ color: GROUND, side: 2, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 2 });
    const strips = new Mesh(sg, sm); strips.frustumCulled = false; strips.renderOrder = -2;
    scene.add(strips, b.line, a.line);
    return { line: a.line, ghostLine: b.line, strips, linePos, ghostPos, stripPos, lineMat: a.mat, ghostMat: b.mat };
  }
  function updateRidges(r: Ridges) {
    const { linePos, ghostPos, stripPos } = r;
    let p = 0;
    for (let ri = 0; ri < R; ri++) {
      const row = rowsY[ri] * G, srow = ri * G;
      for (let x = 0; x < G - 1; x++) {
        linePos[p + 1] = heights[row + x]; linePos[p + 4] = heights[row + x + 1];
        ghostPos[p + 1] = ghost[row + x]; ghostPos[p + 4] = ghost[row + x + 1];
        p += 6;
      }
      for (let x = 0; x < G; x++) stripPos[(srow + x) * 6 + 1] = heights[row + x];
    }
    (r.line.geometry.attributes.instanceStart as any).data.needsUpdate = true;
    (r.ghostLine.geometry.attributes.instanceStart as any).data.needsUpdate = true;
    (r.strips.geometry.attributes.position as BufferAttribute).needsUpdate = true;
    r.lineMat.color.copy(COBALT).lerp(VERMILION, mix);
    r.ghostMat.opacity = GHOST_OPACITY * mix; r.ghostLine.visible = mix > 0.001;
  }

  // ---- style: columns ------------------------------------------------------------------------
  type Columns = { mesh: Mesh; ghostMesh: Mesh; hAttr: InstancedBufferAttribute; gAttr: InstancedBufferAttribute; mat: ShaderMaterial; gmat: ShaderMaterial };
  let columns: Columns | null = null;
  function buildColumns(): Columns {
    const box = new BoxGeometry(0.62, 1, 0.62); box.translate(0, 0.5, 0);
    const offsets = new Float32Array(N * 2);
    for (let y = 0; y < G; y++) for (let x = 0; x < G; x++) { offsets[(y * G + x) * 2] = wx(x); offsets[(y * G + x) * 2 + 1] = wz(y); }
    const make = (opacity: number) => {
      const geo = new InstancedBufferGeometry();
      geo.index = box.index; geo.attributes.position = box.attributes.position; geo.attributes.normal = box.attributes.normal;
      geo.instanceCount = N;
      geo.setAttribute("aOffset", new InstancedBufferAttribute(offsets, 2));
      const h = new InstancedBufferAttribute(new Float32Array(N), 1); h.setUsage(DynamicDrawUsage);
      geo.setAttribute("aHeight", h);
      const mat = new ShaderMaterial({
        uniforms: { uColor: { value: COBALT.clone() }, uOpacity: { value: opacity } },
        transparent: opacity < 1, depthWrite: opacity >= 1,
        vertexShader: `
          attribute vec2 aOffset; attribute float aHeight; varying float vShade;
          void main() {
            vec3 p = position; p.y *= max(aHeight, 0.0); p.x += aOffset.x; p.z += aOffset.y;
            vShade = normal.y > 0.5 ? 1.0 : (abs(normal.x) > 0.5 ? 0.78 : 0.88);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
          }`,
        fragmentShader: `
          uniform vec3 uColor; uniform float uOpacity; varying float vShade;
          void main() { gl_FragColor = vec4(mix(vec3(1.0), uColor, vShade), uOpacity); }`,
      });
      const mesh = new Mesh(geo, mat); mesh.frustumCulled = false;
      return { mesh, h, mat };
    };
    const a = make(1), b = make(0); b.mesh.visible = false; b.mesh.renderOrder = 1;
    scene.add(a.mesh, b.mesh);
    return { mesh: a.mesh, ghostMesh: b.mesh, hAttr: a.h, gAttr: b.h, mat: a.mat, gmat: b.mat };
  }
  function updateColumns(c: Columns) {
    (c.hAttr.array as Float32Array).set(heights); c.hAttr.needsUpdate = true;
    (c.gAttr.array as Float32Array).set(ghost); c.gAttr.needsUpdate = true;
    (c.mat.uniforms.uColor.value as Color).copy(COBALT).lerp(VERMILION, mix);
    c.gmat.uniforms.uOpacity.value = GHOST_OPACITY * mix; c.ghostMesh.visible = mix > 0.001;
  }

  if (opts.style === "columns") columns = buildColumns(); else ridges = buildRidges();

  // ---- camera ----------------------------------------------------------------------------------
  function placeCamera() {
    const aspect = camera.aspect;
    // distance so that the 200-unit grid fits the width with a small margin
    const fovH = 2 * Math.atan(Math.tan((camera.fov * Math.PI) / 360) * aspect);
    const dist = Math.max(200, (G * 0.57) / Math.tan(fovH / 2)) * (aspect < 1 ? 1.2 : 1) * distScale;
    const sp = Math.sin(polar), cp = Math.cos(polar);
    camera.position.set(dist * sp * Math.sin(azimuth), dist * cp, dist * sp * Math.cos(azimuth));
    camera.lookAt(0, HEIGHT * 0.3, 0);
  }
  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (w === 0 || h === 0) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
    const res = new Vector2(w * renderer.getPixelRatio(), h * renderer.getPixelRatio());
    if (ridges) { ridges.lineMat.resolution.copy(res); ridges.ghostMat.resolution.copy(res); }
    placeCamera(); needRender = true;
  }
  const ro = new ResizeObserver(resize); ro.observe(canvas);

  // ---- interaction: drag to rotate with damping, no wheel, no scroll hijack --------------------
  let pointerId = -1, lastX = 0, lastY = 0;
  function endIntro() { if (introStart >= 0) { introStart = -1; distScale = 1; placeCamera(); } }
  function onDown(e: PointerEvent) {
    if (e.button !== 0 && e.pointerType === "mouse") return;
    endIntro();
    pointerId = e.pointerId; lastX = e.clientX; lastY = e.clientY; azVel = 0; polVel = 0; dragged = true;
    canvas.setPointerCapture(e.pointerId); canvas.classList.add("is-dragging");
  }
  function onMove(e: PointerEvent) {
    if (e.pointerId !== pointerId) return;
    const dx = e.clientX - lastX, dy = e.clientY - lastY; lastX = e.clientX; lastY = e.clientY;
    azVel = -dx * 0.004; polVel = -dy * 0.003;
    azimuth += azVel; polar = clamp(polar + polVel, POLAR_MIN, POLAR_MAX);
    placeCamera(); needRender = true;
  }
  function onUp(e: PointerEvent) {
    if (e.pointerId !== pointerId) return;
    pointerId = -1; canvas.classList.remove("is-dragging");
    try { canvas.releasePointerCapture(e.pointerId); } catch {}
  }
  canvas.addEventListener("pointerdown", onDown); canvas.addEventListener("pointermove", onMove);
  canvas.addEventListener("pointerup", onUp); canvas.addEventListener("pointercancel", onUp);
  canvas.addEventListener("webglcontextlost", (e) => { e.preventDefault(); lost = true; pause(); opts.onLost(); });

  // ---- loop ----------------------------------------------------------------------------------
  function frame(ts: number) {
    raf = 0;
    if (disposed || lost) return;
    const dt = lastTs ? Math.min((ts - lastTs) / 1000, 0.1) : 0; lastTs = ts;
    let moving = false;
    if (playing) { slot = (slot + dt * SLOTS_PER_SECOND) % SLOTS; opts.onTime(slot); moving = true; }
    if (mix !== mixTarget) {
      const step = dt * (1000 / MORPH_MS);
      mix = mixTarget > mix ? Math.min(mixTarget, mix + step) : Math.max(mixTarget, mix - step); moving = true;
    }
    if (introStart >= 0) {
      // entry move: ease from far away, behind and steeper, through half a turn into the default view
      const u = clamp((ts - introStart) / INTRO_MS, 0, 1), e = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
      azimuth = -Math.PI + Math.PI * e; distScale = 2.6 - 1.6 * e; polar = POLAR_DEFAULT - 0.22 * (1 - e);
      placeCamera(); moving = true;
      if (u >= 1) { introStart = -1; distScale = 1; }
    } else if (pointerId < 0 && (Math.abs(azVel) > 1e-4 || Math.abs(polVel) > 1e-4)) {
      azVel *= 0.92; polVel *= 0.92;
      azimuth += azVel; polar = clamp(polar + polVel, POLAR_MIN, POLAR_MAX);
      placeCamera(); moving = true;
    } else if (opts.idleRotation && !dragged && pointerId < 0) {
      azimuth += IDLE_SPEED * dt; placeCamera(); moving = true;
    }
    if (moving || needRender) {
      computeHeights();
      if (ridges) updateRidges(ridges); else if (columns) updateColumns(columns);
      renderer.render(scene, camera); needRender = false;
    }
    if (moving || playing) raf = requestAnimationFrame(frame); else lastTs = 0;
  }
  function kick() { if (!raf && !disposed) raf = requestAnimationFrame(frame); }
  function play() { if (lost) return; playing = true; kick(); }
  function pause() { playing = false; lastTs = 0; }

  if (opts.idleRotation) { introStart = performance.now(); azimuth = -Math.PI; distScale = 2.6; polar = POLAR_DEFAULT - 0.22; }
  resize(); computeHeights();
  if (ridges) updateRidges(ridges); else if (columns) updateColumns(columns);
  renderer.render(scene, camera);
  opts.onReady(); opts.onTime(slot);
  if (opts.autoplay) play(); else if (opts.idleRotation) kick();

  return {
    play, pause, playing: () => playing,
    seek(s: number) { slot = ((s % SLOTS) + SLOTS) % SLOTS; opts.onTime(slot); needRender = true; kick(); },
    slot: () => slot,
    setCondition(e: boolean) { emergency = e; mixTarget = e ? 1 : 0; kick(); },
    still(s: number) {
      const keep = { slot, azimuth, polar, mix, distScale };
      const pr = renderer.getPixelRatio(); renderer.setPixelRatio(2); resize();
      slot = s; azimuth = 0; polar = POLAR_DEFAULT; mix = mixTarget; distScale = 1; placeCamera(); computeHeights();
      if (ridges) updateRidges(ridges); else if (columns) updateColumns(columns);
      renderer.render(scene, camera);
      const data = canvas.toDataURL("image/png");
      renderer.setPixelRatio(pr); resize();
      slot = keep.slot; azimuth = keep.azimuth; polar = keep.polar; mix = keep.mix; distScale = keep.distScale; placeCamera(); needRender = true; kick();
      return data;
    },
    dispose() {
      disposed = true; pause(); ro.disconnect();
      if (raf) cancelAnimationFrame(raf);
      scene.traverse((o: any) => { o.geometry?.dispose?.(); o.material?.dispose?.(); });
      renderer.dispose();
    },
  };
}

function clamp(v: number, lo: number, hi: number) { return v < lo ? lo : v > hi ? hi : v; }
