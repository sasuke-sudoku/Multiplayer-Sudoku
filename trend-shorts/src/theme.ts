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

// Per-episode look. Every option keeps the white, gradient-free base; they change accent, texture and motion.
export const palettes = {
  blue: { accent: "#0a5cff", fill: "#eef3ff", border: "#9db7f5", label: "#1d3b80" },
  green: { accent: "#0a8f4e", fill: "#eaf7f0", border: "#8fd0ad", label: "#0d4d2e" },
  orange: { accent: "#e2580b", fill: "#fff3e9", border: "#f4b88c", label: "#7a2f00" },
  purple: { accent: "#6d28d9", fill: "#f3eeff", border: "#c3a8f3", label: "#3b1677" },
  teal: { accent: "#0e7490", fill: "#e8f6f8", border: "#8fcbd6", label: "#134e5e" },
} as const;

export type EpisodeStyle = {
  palette: keyof typeof palettes;
  pattern: "grid" | "dots" | "stripes" | "plain";
  motion: "pop" | "slide" | "zoom" | "wipe";
  caption: "marker" | "box" | "underline";
  header: "center" | "left";
};
export const style: EpisodeStyle = {
  palette: "blue",
  pattern: "grid",
  motion: "pop",
  caption: "marker",
  header: "center",
  ...((timeline as { style?: Partial<EpisodeStyle> }).style ?? {}),
};
const pal = palettes[style.palette];

export const colors = {
  bg: "#ffffff",
  accent: pal.accent,
  accent2: pal.accent,
  highlight: "#ffd400",
  danger: "#e8173b",
  text: "#111111",
  muted: "#3a404d",
  card: "#f1f3f7",
  cardBorder: "#c4cad6",
  // Tinted card fills so the contents stand apart from the white background.
  blueFill: pal.fill,
  blueBorder: pal.border,
  blueLabel: pal.label,
  redFill: "#fff0f2",
  redBorder: "#f2a1af",
  redLabel: "#9b1c33",
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
export const series: string = timeline.series;

// Optional photos in public/ (paths relative to public/). Empty string = use the built-in fallback.
export const images: { founder: string; logo: string; site: string } = timeline.images;

type Item = { label: string; value: string; tone?: "blue" | "red" };
// Data for each scene type. An episode lists scenes as { id, type, data } in any order.
export type SceneData = {
  stats: { stats: Item[]; tagline: string };
  profile: { name: string; emoji: string; rows: { label: string; value: string }[]; chips: string[]; chipMark: string };
  reveal: { date: string; name: string; flow: string[]; pill: string };
  growth: { main: Item; cards: Item[] };
  grid: { tasks: string[]; taskTag: string; stamp: string };
  warning: { header: string; warnLabel: string; warn: string; after: string; afterHighlight: string };
  question: { question: string[]; questionHighlight: string; comment: string };
  bigtext: { kicker?: string; lines: string[]; highlight?: string; tone?: "blue" | "red" };
  versus: { before: Item; after: Item; arrow?: string };
  ranking: { title: string; items: { label: string; value: string }[] };
  quiz: { question: string; choices: string[]; answer: number; note?: string };
  timeline: { events: { date: string; text: string; tone?: "blue" | "red" }[] };
  quote: { quote: string; by: string; highlight?: string };
  chart: { label: string; unit: string; points: { x: string; y: number }[] };
};
export type SceneDef = { [K in keyof SceneData]: { id: string; type: K; data: SceneData[K] } }[keyof SceneData];
export const sceneDefs = timeline.scenes as SceneDef[];
