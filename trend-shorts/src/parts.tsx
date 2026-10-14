import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { colors, fontFamily, series, style, title, TimedLine } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const usePop = (start: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - start, fps, config: { damping: 12, stiffness: 160 } });
};

export const Pop: React.FC<{ start: number; children: React.ReactNode; style?: React.CSSProperties }> = ({
  start,
  children,
  style,
}) => {
  const p = usePop(start);
  return (
    <div style={{ opacity: Math.min(1, p * 2), scale: String(0.6 + 0.4 * p), ...style }}>{children}</div>
  );
};

export const CountUp: React.FC<{ start: number; to: number; duration?: number; decimals?: number }> = ({
  start,
  to,
  duration = 20,
  decimals = 0,
}) => {
  const frame = useCurrentFrame();
  const v = interpolate(frame, [start, start + duration], [0, to], {
    ...clamp,
    easing: Easing.out(Easing.cubic),
  });
  return <>{v.toLocaleString("ja-JP", { maximumFractionDigits: decimals, minimumFractionDigits: decimals })}</>;
};

const svgUrl = (svg: string) => `url("data:image/svg+xml;utf8,${encodeURIComponent(svg)}")`;
const patterns: Record<string, { image: string; size: number } | null> = {
  grid: {
    image: svgUrl('<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90"><path d="M0 1H90M1 0V90" stroke="rgba(0,0,0,0.05)" stroke-width="2"/></svg>'),
    size: 90,
  },
  dots: {
    image: svgUrl('<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60"><circle cx="30" cy="30" r="4" fill="rgba(0,0,0,0.08)"/></svg>'),
    size: 60,
  },
  stripes: {
    image: svgUrl('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><path d="M-20 100L100 -20M-60 60L60 -60M20 140L140 20" stroke="rgba(0,0,0,0.04)" stroke-width="16"/></svg>'),
    size: 80,
  },
  plain: null,
};

export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const pattern = patterns[style.pattern];
  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg }}>
      {pattern ? (
        <AbsoluteFill
          style={{
            backgroundImage: pattern.image,
            backgroundSize: `${pattern.size}px ${pattern.size}px`,
            backgroundPosition: `0px ${(frame * 1.5) % pattern.size}px`,
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};

// How each scene enters (style.motion).
export const SceneEnter: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const e = interpolate(frame, [0, 10], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const byType: Record<string, React.CSSProperties> = {
    pop: { opacity: e, scale: String(0.94 + 0.06 * e) },
    slide: { translate: `${(1 - e) * 1080}px 0px` },
    zoom: { opacity: e, scale: String(1.18 - 0.18 * e) },
    wipe: { clipPath: `inset(0 ${(1 - e) * 100}% 0 0)` },
  };
  return <AbsoluteFill style={byType[style.motion]}>{children}</AbsoluteFill>;
};

export const Header: React.FC = () => {
  const p = usePop(0);
  const [q, rest] = [title.split("？")[0], title.split("？")[1]];
  if (style.header === "left") {
    return (
      <div
        style={{
          position: "absolute",
          top: 120,
          left: 80,
          right: 80,
          borderLeft: `14px solid ${colors.accent}`,
          paddingLeft: 30,
          opacity: p,
          translate: `${(1 - p) * -60}px 0px`,
        }}
      >
        <div style={{ color: colors.danger, fontSize: 38, fontWeight: 900, letterSpacing: 2 }}>{series}</div>
        <div style={{ color: colors.text, fontSize: 60, fontWeight: 900, lineHeight: 1.25 }}>
          {q}？
          <br />
          <span style={{ color: colors.accent }}>{rest}</span>
        </div>
      </div>
    );
  }
  return (
    <div
      style={{
        position: "absolute",
        top: 130,
        left: 80,
        right: 80,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 22,
        opacity: p,
        translate: `0px ${(1 - p) * -40}px`,
      }}
    >
      <div
        style={{
          background: colors.danger,
          color: "white",
          fontSize: 40,
          fontWeight: 900,
          padding: "8px 30px",
          borderRadius: 999,
          letterSpacing: 2,
        }}
      >
        {series}
      </div>
      <div
        style={{
          color: colors.text,
          fontSize: 58,
          fontWeight: 900,
          textAlign: "center",
          lineHeight: 1.25,
        }}
      >
        {q}？
        <br />
        <span style={{ color: colors.accent }}>{rest}</span>
      </div>
    </div>
  );
};

const highlightStyle: Record<string, React.CSSProperties> = {
  marker: { background: colors.highlight, padding: "0 8px", borderRadius: 8 },
  box: { color: colors.highlight },
  underline: { color: colors.accent, textDecoration: `underline 10px ${colors.highlight}`, textUnderlineOffset: 10 },
};

const renderHighlighted = (text: string, highlight: string[]) => {
  if (highlight.length === 0) return text;
  const pattern = new RegExp(`(${highlight.map((h) => h.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`);
  return text.split(pattern).map((part, i) =>
    highlight.includes(part) ? (
      <span key={i} style={highlightStyle[style.caption]}>
        {part}
      </span>
    ) : (
      <React.Fragment key={i}>{part}</React.Fragment>
    ),
  );
};

export const Caption: React.FC<{ line: TimedLine }> = ({ line }) => {
  const frame = useCurrentFrame();
  const p = spring({ frame, fps: 30, config: { damping: 14, stiffness: 220 } });
  return (
    <div
      style={{
        position: "absolute",
        top: 1290,
        left: 70,
        right: 70,
        display: "flex",
        justifyContent: "center",
        opacity: interpolate(frame, [0, 4], [0, 1], clamp),
        scale: String(0.85 + 0.15 * p),
      }}
    >
      <div
        style={{
          color: style.caption === "box" ? "#fff" : colors.text,
          background: style.caption === "box" ? "rgba(17,17,17,0.9)" : undefined,
          padding: style.caption === "box" ? "14px 32px" : undefined,
          borderRadius: 24,
          fontSize: 58,
          fontWeight: 900,
          lineHeight: 1.35,
          textAlign: "center",
          whiteSpace: "pre-line",
        }}
      >
        {renderHighlighted(line.text, line.highlight)}
      </div>
    </div>
  );
};

export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; tone?: "blue" | "red" }> = ({
  children,
  style,
  tone = "blue",
}) => (
  <div
    style={{
      background: tone === "red" ? colors.redFill : colors.blueFill,
      border: `3px solid ${tone === "red" ? colors.redBorder : colors.blueBorder}`,
      boxShadow: "0 8px 20px rgba(17,17,17,0.08)",
      borderRadius: 36,
      padding: "28px 40px",
      color: colors.text,
      fontFamily,
      ...style,
    }}
  >
    {children}
  </div>
);

// Small solid label used inside cards.
export const Tag: React.FC<{ children: React.ReactNode; tone?: "blue" | "red"; style?: React.CSSProperties }> = ({
  children,
  tone = "blue",
  style,
}) => (
  <span
    style={{
      display: "inline-block",
      background: tone === "red" ? colors.danger : colors.accent,
      color: "#fff",
      fontWeight: 900,
      borderRadius: 12,
      padding: "4px 16px",
      ...style,
    }}
  >
    {children}
  </span>
);
