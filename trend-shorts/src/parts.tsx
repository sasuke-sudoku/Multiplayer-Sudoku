import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { colors, fontFamily, series, title, TimedLine } from "./theme";

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

export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg }}>
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(0,0,0,0.03) 2px, transparent 2px), linear-gradient(90deg, rgba(0,0,0,0.03) 2px, transparent 2px)",
          backgroundSize: "90px 90px",
          backgroundPosition: `0px ${(frame * 1.5) % 90}px`,
        }}
      />
    </AbsoluteFill>
  );
};

export const Header: React.FC = () => {
  const p = usePop(0);
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
        {title.split("？")[0]}？
        <br />
        <span style={{ color: colors.accent }}>{title.split("？")[1]}</span>
      </div>
    </div>
  );
};

const renderHighlighted = (text: string, highlight: string[]) => {
  if (highlight.length === 0) return text;
  const pattern = new RegExp(`(${highlight.map((h) => h.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`);
  return text.split(pattern).map((part, i) =>
    highlight.includes(part) ? (
      <span key={i} style={{ background: colors.highlight, padding: "0 8px", borderRadius: 8 }}>
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
          color: colors.text,
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
