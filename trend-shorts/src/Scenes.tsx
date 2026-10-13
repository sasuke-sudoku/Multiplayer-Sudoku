import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { Card, CountUp, Pop, Tag, usePop } from "./parts";
import { colors, images, SceneTiming, visuals } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Start frame of the scene's second narration line (falls back to 1s in).
const secondLine = (s: SceneTiming) => s.lines[1]?.from ?? 30;
// Spread n items evenly over the scene's first narration line.
const stagger = (s: SceneTiming, n: number, offset = 2) => (i: number) =>
  offset + i * Math.floor((s.lines[0].duration - offset) / Math.max(1, n));

// "約375億円" → counts up the number, keeps the prefix/suffix. Values without a number render as-is.
const Value: React.FC<{ value: string; start: number; duration?: number }> = ({ value, start, duration }) => {
  const m = value.match(/^(\D*?)(\d+(?:\.\d+)?)(.*)$/);
  if (!m) return <>{value}</>;
  const decimals = m[2].includes(".") ? m[2].split(".")[1].length : 0;
  return (
    <>
      {m[1]}
      <CountUp start={start} to={Number(m[2])} duration={duration} decimals={decimals} />
      {m[3]}
    </>
  );
};

const highlightIn = (text: string, word: string, color: string) => {
  const i = word ? text.indexOf(word) : -1;
  if (i < 0) return text;
  return (
    <>
      {text.slice(0, i)}
      <span style={{ color }}>{word}</span>
      {text.slice(i + word.length)}
    </>
  );
};

// Visual stage between the header and the captions.
const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill
    style={{
      top: 440,
      height: 760,
      left: 80,
      right: 80,
      width: "auto",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: 28,
    }}
  >
    {children}
  </AbsoluteFill>
);

const Stat: React.FC<{ start: number; label: string; children: React.ReactNode; color?: string }> = ({
  start,
  label,
  children,
  color = colors.accent,
}) => (
  <Pop start={start} style={{ width: "100%" }}>
    <Card
      tone={color === colors.danger ? "red" : "blue"}
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        borderLeft: `16px solid ${color === colors.danger ? colors.danger : colors.accent}`,
      }}
    >
      <span style={{ fontSize: 52, fontWeight: 900, color: color === colors.danger ? colors.redLabel : colors.blueLabel }}>
        {label}
      </span>
      <span style={{ fontSize: 104, fontWeight: 900, color, lineHeight: 1.1 }}>{children}</span>
    </Card>
  </Pop>
);

const Hook: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const v = visuals.hook;
  const at = stagger(s, v.stats.length);
  return (
    <Stage>
      {v.stats.map((stat, i) => (
        <Stat key={stat.label} start={at(i)} label={stat.label} color={stat.tone === "red" ? colors.danger : colors.accent}>
          <Value value={stat.value} start={at(i)} />
        </Stat>
      ))}
      {v.tagline ? (
        <Pop start={secondLine(s) + 4}>
          <div style={{ fontSize: 56, fontWeight: 900, color: colors.accent2 }}>{v.tagline}</div>
        </Pop>
      ) : null}
    </Stage>
  );
};

const ProfileRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div style={{ display: "flex", gap: 20, fontSize: 44, lineHeight: 1.45 }}>
    <Tag style={{ fontSize: 34, width: 110, textAlign: "center", flexShrink: 0, alignSelf: "center" }}>{label}</Tag>
    <span style={{ color: colors.text, fontWeight: 900 }}>{value}</span>
  </div>
);

const Who: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const v = visuals.who;
  const t = secondLine(s);
  return (
    <Stage>
      <Pop start={0} style={{ width: "100%" }}>
        <Card style={{ padding: "34px 36px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 30, marginBottom: 20 }}>
            <div
              style={{
                width: 150,
                height: 150,
                borderRadius: "50%",
                background: colors.accent2,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 90,
                flexShrink: 0,
              }}
            >
              {images.founder ? (
                <Img
                  src={staticFile(images.founder)}
                  style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: "50%" }}
                />
              ) : (
                v.emoji
              )}
            </div>
            <div>
              <div style={{ fontSize: 34, fontWeight: 700, color: colors.accent }}>PROFILE</div>
              <div style={{ fontSize: 78, fontWeight: 900, lineHeight: 1.1 }}>{v.name}</div>
            </div>
          </div>
          {v.rows.map((row) => (
            <ProfileRow key={row.label} label={row.label} value={row.value} />
          ))}
        </Card>
      </Pop>
      <div style={{ display: "flex", gap: 24 }}>
        {v.chips.map((name, i) => (
          <Pop key={name} start={t + 6 + i * 8}>
            <Card tone="red" style={{ padding: "16px 26px", textAlign: "center" }}>
              <div style={{ fontSize: 40, fontWeight: 900, color: colors.redLabel }}>{name}</div>
              <div style={{ fontSize: 72, fontWeight: 900, color: colors.danger, lineHeight: 1 }}>{v.chipMark}</div>
            </Card>
          </Pop>
        ))}
      </div>
    </Stage>
  );
};

const Launch: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const v = visuals.launch;
  const t = secondLine(s);
  return (
    <Stage>
      <Pop start={4}>
        <div style={{ fontSize: 48, fontWeight: 700, color: colors.muted, textAlign: "center" }}>{v.date}</div>
      </Pop>
      <Pop start={14}>
        {images.logo ? (
          <Img src={staticFile(images.logo)} style={{ height: images.site ? 90 : 180, objectFit: "contain" }} />
        ) : (
          <div style={{ fontSize: images.site ? 100 : 170, fontWeight: 900, color: colors.text, letterSpacing: 4 }}>
            {v.name}
          </div>
        )}
      </Pop>
      {images.site ? (
        <Pop start={20}>
          <Img
            src={staticFile(images.site)}
            style={{
              width: 880,
              height: 240,
              objectFit: "cover",
              objectPosition: "top",
              borderRadius: 24,
              border: `3px solid ${colors.cardBorder}`,
            }}
          />
        </Pop>
      ) : null}
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        {v.flow.map((step, i) => (
          <React.Fragment key={step}>
            {i > 0 ? (
              <Pop start={t + 4 + i * 16 - 6}>
                <div style={{ fontSize: 70, color: colors.accent }}>→</div>
              </Pop>
            ) : null}
            <Pop start={t + 4 + i * 16}>
              <Card style={{ fontSize: 52, fontWeight: 900 }}>{step}</Card>
            </Pop>
          </React.Fragment>
        ))}
      </div>
      <Pop start={t + 4 + v.flow.length * 16}>
        <div
          style={{
            background: colors.accent,
            color: "#fff",
            fontSize: 56,
            fontWeight: 900,
            padding: "12px 40px",
            borderRadius: 20,
          }}
        >
          {v.pill}
        </div>
      </Pop>
    </Stage>
  );
};

const Growth: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const v = visuals.growth;
  const frame = useCurrentFrame();
  const t = secondLine(s);
  const bars = [0.08, 0.16, 0.3, 0.5, 0.75, 1];
  return (
    <Stage>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 22, height: 220 }}>
        {bars.map((h, i) => (
          <div
            key={i}
            style={{
              width: 90,
              borderRadius: "16px 16px 0 0",
              background: i === bars.length - 1 ? colors.accent : colors.accent2,
              height: interpolate(frame, [i * 5, i * 5 + 25], [0, h * 220], clamp),
            }}
          />
        ))}
      </div>
      <Pop start={12} style={{ width: "100%" }}>
        <Card style={{ textAlign: "center" }}>
          <div style={{ fontSize: 46, fontWeight: 900, color: colors.blueLabel }}>{v.main.label}</div>
          <div style={{ fontSize: 120, fontWeight: 900, color: colors.accent, lineHeight: 1.1 }}>
            <Value value={v.main.value} start={12} duration={30} />
          </div>
        </Card>
      </Pop>
      <div style={{ display: "flex", gap: 24, width: "100%" }}>
        {v.cards.map((card, i) => (
          <Pop key={card.label} start={t + 6 + i * 34} style={{ flex: 1 }}>
            <Card tone={card.tone ?? "blue"} style={{ textAlign: "center", padding: "22px 10px" }}>
              <Tag tone={card.tone ?? "blue"} style={{ fontSize: 38 }}>
                {card.label}
              </Tag>
              <div style={{ fontSize: 76, fontWeight: 900, color: card.tone === "red" ? colors.danger : colors.text }}>
                {card.value}
              </div>
            </Card>
          </Pop>
        ))}
      </div>
    </Stage>
  );
};

const How: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const v = visuals.how;
  const t = secondLine(s);
  const tasks = v.tasks;
  const at = stagger(s, tasks.length, 4);
  const stamp = usePop(t + 4);
  return (
    <Stage>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, width: "100%" }}>
        {tasks.map((task, i) => (
          <Pop key={task} start={at(i)}>
            <Card style={{ fontSize: 50, fontWeight: 900, textAlign: "center", padding: "30px 10px" }}>
              {task}
              <Tag style={{ fontSize: 38, marginTop: 12 }}>{v.taskTag}</Tag>
            </Card>
          </Pop>
        ))}
      </div>
      <div
        style={{
          opacity: Math.min(1, stamp * 2),
          scale: String(2 - stamp),
          rotate: "-6deg",
          border: `10px solid ${colors.danger}`,
          color: colors.danger,
          fontSize: 92,
          fontWeight: 900,
          padding: "6px 40px",
          borderRadius: 24,
          marginTop: 20,
        }}
      >
        {v.stamp}
      </div>
    </Stage>
  );
};

const Shadow: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const v = visuals.shadow;
  const frame = useCurrentFrame();
  const t = secondLine(s);
  const shake = frame < 20 ? Math.sin(frame * 2.2) * (20 - frame) * 0.8 : 0;
  return (
    <Stage>
      <Pop start={0}>
        <div style={{ fontSize: 60, fontWeight: 900, color: colors.danger }}>{v.header}</div>
      </Pop>
      <div style={{ translate: `${shake}px 0px`, width: "100%" }}>
        <Card tone="red" style={{ textAlign: "center", borderColor: colors.danger }}>
          <div style={{ fontSize: 48, fontWeight: 900, color: colors.redLabel }}>{v.warnLabel}</div>
          <div style={{ fontSize: 112, fontWeight: 900, color: colors.danger, lineHeight: 1.1 }}>{v.warn}</div>
        </Card>
      </div>
      <Pop start={t + 4}>
        <div style={{ fontSize: 70, color: colors.accent }}>↓</div>
      </Pop>
      <Pop start={t + 10} style={{ width: "100%" }}>
        <Card style={{ textAlign: "center", borderColor: colors.accent }}>
          <div style={{ fontSize: 60, fontWeight: 900 }}>{highlightIn(v.after, v.afterHighlight, colors.accent)}</div>
        </Card>
      </Pop>
    </Stage>
  );
};

const Outro: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const v = visuals.outro;
  const frame = useCurrentFrame();
  const t = secondLine(s);
  const pressed = frame > t + 40 && frame < t + 52;
  const subscribed = frame >= t + 52;
  return (
    <Stage>
      <Pop start={2}>
        <div style={{ fontSize: 100, fontWeight: 900, color: colors.text, textAlign: "center", lineHeight: 1.3 }}>
          {v.question.map((line, i) => (
            <div key={i}>{highlightIn(line, v.questionHighlight, colors.accent)}</div>
          ))}
        </div>
      </Pop>
      <Pop start={8}>
        <div style={{ fontSize: 48, fontWeight: 700, color: colors.muted }}>{v.comment}</div>
      </Pop>
      <Pop start={t + 4}>
        <div
          style={{
            marginTop: 30,
            background: subscribed ? "#555" : "#ff0000",
            color: "white",
            fontSize: 64,
            fontWeight: 900,
            padding: "22px 60px",
            borderRadius: 999,
            scale: pressed ? "0.9" : "1",
            boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
          }}
        >
          {subscribed ? "✔ 登録済み" : "チャンネル登録"}
        </div>
      </Pop>
      <div
        style={{
          fontSize: 90,
          opacity: interpolate(frame, [t + 24, t + 30], [0, 1], clamp),
          translate: `${interpolate(frame, [t + 24, t + 40], [160, 40], clamp)}px ${interpolate(frame, [t + 24, t + 40], [120, -70], clamp)}px`,
          height: 0,
        }}
      >
        👆
      </div>
    </Stage>
  );
};

export const sceneComponents: Record<string, React.FC<{ s: SceneTiming }>> = {
  hook: Hook,
  who: Who,
  launch: Launch,
  growth: Growth,
  how: How,
  shadow: Shadow,
  outro: Outro,
};
