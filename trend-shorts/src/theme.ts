import "@fontsource/noto-sans-jp/700.css";
import "@fontsource/noto-sans-jp/900.css";
import timeline from "./timeline.json";

// Bundled from npm so rendering never depends on fetching fonts at runtime.
export const fontFamily = "'Noto Sans JP', sans-serif";

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
// Extra hold after the last line so the subscribe call can breathe.
export const OUTRO_TAIL = 1.5 * FPS;

export const colors = {
  bg1: "#0b1026",
  bg2: "#1b0f3b",
  accent: "#ffd400",
  accent2: "#00e0ff",
  danger: "#ff3b5c",
  text: "#ffffff",
  muted: "#a9b3d6",
  card: "rgba(255,255,255,0.08)",
  cardBorder: "rgba(255,255,255,0.18)",
};

export type Line = {
  scene: string;
  text: string;
  reading: string;
  highlight: string[];
  file: string;
  seconds: number;
};

export type TimedLine = Line & { from: number; duration: number };

// Lay the narration lines end to end on the frame timeline.
export const lines: TimedLine[] = (() => {
  let cursor = 0;
  return (timeline.lines as Line[]).map((line) => {
    const duration = Math.round(line.seconds * FPS);
    const timed = { ...line, from: cursor, duration };
    cursor += duration;
    return timed;
  });
})();

export const narrationFrames = lines.reduce((sum, l) => sum + l.duration, 0);
export const totalFrames = narrationFrames + OUTRO_TAIL;

export type SceneTiming = { id: string; from: number; duration: number; lines: TimedLine[] };

// Group consecutive lines with the same scene id. Line offsets are scene-relative.
export const scenes: SceneTiming[] = (() => {
  const result: SceneTiming[] = [];
  for (const line of lines) {
    const last = result[result.length - 1];
    if (last && last.id === line.scene) {
      last.duration += line.duration;
      last.lines.push({ ...line, from: line.from - last.from });
    } else {
      result.push({ id: line.scene, from: line.from, duration: line.duration, lines: [{ ...line, from: 0 }] });
    }
  }
  result[result.length - 1].duration += OUTRO_TAIL;
  return result;
})();

export const title: string = timeline.title;
export const source: string = timeline.source;
