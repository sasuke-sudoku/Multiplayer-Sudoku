import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Card, CountUp, Pop, usePop } from "./parts";
import { colors, SceneTiming } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

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
    <Card style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <span style={{ fontSize: 52, fontWeight: 700, color: colors.muted }}>{label}</span>
      <span style={{ fontSize: 104, fontWeight: 900, color, lineHeight: 1.1 }}>{children}</span>
    </Card>
  </Pop>
);

const Hook: React.FC<{ s: SceneTiming }> = ({ s }) => (
  <Stage>
    <Stat start={2} label="社員">0人</Stat>
    <Stat start={30} label="顧客">
      <CountUp start={30} to={1} />
      万人
    </Stat>
    <Stat start={62} label="売上（見込み）" color={colors.danger}>
      <CountUp start={62} to={15} />
      億円
    </Stat>
    <Pop start={s.lines[1].from + 4}>
      <div style={{ fontSize: 56, fontWeight: 900, color: colors.accent2 }}>たった1人のAI会社</div>
    </Pop>
  </Stage>
);

const ProfileRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div style={{ display: "flex", gap: 20, fontSize: 40, lineHeight: 1.45 }}>
    <span style={{ color: colors.muted, fontWeight: 700, width: 110, flexShrink: 0 }}>{label}</span>
    <span style={{ color: colors.text, fontWeight: 900 }}>{value}</span>
  </div>
);

const Who: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const t = s.lines[1].from;
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
              👨‍💻
            </div>
            <div>
              <div style={{ fontSize: 34, fontWeight: 700, color: colors.accent }}>PROFILE</div>
              <div style={{ fontSize: 78, fontWeight: 900, lineHeight: 1.1 }}>Ben Broca</div>
            </div>
          </div>
          <ProfileRow label="年齢" value="40歳" />
          <ProfileRow label="会社" value="Polsia（創業者）" />
          <ProfileRow label="経歴" value="CloudKitchens／Hutch共同創業" />
        </Card>
      </Pop>
      <div style={{ display: "flex", gap: 24 }}>
        {["AIソフト①", "AIソフト②", "AIソフト③"].map((name, i) => (
          <Pop key={name} start={t + 6 + i * 8}>
            <Card style={{ padding: "16px 26px", textAlign: "center" }}>
              <div style={{ fontSize: 36, fontWeight: 700, color: colors.muted }}>{name}</div>
              <div style={{ fontSize: 72, fontWeight: 900, color: colors.danger, lineHeight: 1 }}>✕</div>
            </Card>
          </Pop>
        ))}
      </div>
    </Stage>
  );
};

const Launch: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const t = s.lines[1].from;
  const frame = useCurrentFrame();
  return (
    <Stage>
      <Pop start={4}>
        <div style={{ fontSize: 48, fontWeight: 700, color: colors.muted, textAlign: "center" }}>2025.12 公開</div>
      </Pop>
      <Pop start={14}>
        <div
          style={{
            fontSize: 170,
            fontWeight: 900,
            color: colors.text,
            letterSpacing: 4,
            textShadow: `0 0 ${30 + 10 * Math.sin(frame / 6)}px ${colors.accent2}`,
          }}
        >
          Polsia
        </div>
      </Pop>
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        <Pop start={t + 4}>
          <Card style={{ fontSize: 52, fontWeight: 900 }}>立ち上げ</Card>
        </Pop>
        <Pop start={t + 14}>
          <div style={{ fontSize: 70, color: colors.accent }}>→</div>
        </Pop>
        <Pop start={t + 20}>
          <Card style={{ fontSize: 52, fontWeight: 900 }}>運営</Card>
        </Pop>
      </div>
      <Pop start={t + 32}>
        <div
          style={{
            background: colors.accent,
            color: "#000",
            fontSize: 56,
            fontWeight: 900,
            padding: "12px 40px",
            borderRadius: 20,
          }}
        >
          🤖 AIがまるごと代行
        </div>
      </Pop>
    </Stage>
  );
};

const Growth: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const frame = useCurrentFrame();
  const t = s.lines[1].from;
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
          <div style={{ fontSize: 46, fontWeight: 700, color: colors.muted }}>約半年で 企業評価額（※売上ではない）</div>
          <div style={{ fontSize: 120, fontWeight: 900, color: colors.accent, lineHeight: 1.1 }}>
            約<CountUp start={12} to={375} duration={30} />億円
          </div>
        </Card>
      </Pop>
      <div style={{ display: "flex", gap: 24, width: "100%" }}>
        <Pop start={t + 6} style={{ flex: 1 }}>
          <Card style={{ textAlign: "center", padding: "22px 10px" }}>
            <div style={{ fontSize: 40, color: colors.muted, fontWeight: 700 }}>有料顧客</div>
            <div style={{ fontSize: 76, fontWeight: 900 }}>1万人</div>
          </Card>
        </Pop>
        <Pop start={t + 40} style={{ flex: 1 }}>
          <Card style={{ textAlign: "center", padding: "22px 10px" }}>
            <div style={{ fontSize: 40, color: colors.muted, fontWeight: 700 }}>今年の売上見込み</div>
            <div style={{ fontSize: 76, fontWeight: 900, color: colors.danger }}>約15億円</div>
          </Card>
        </Pop>
      </div>
    </Stage>
  );
};

const How: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const t = s.lines[1].from;
  const tasks = ["📧 メール返信", "💻 コード修正", "💬 問い合わせ", "💸 返金処理"];
  const stamp = usePop(t + 4);
  return (
    <Stage>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, width: "100%" }}>
        {tasks.map((task, i) => (
          <Pop key={task} start={4 + i * 22}>
            <Card style={{ fontSize: 50, fontWeight: 900, textAlign: "center", padding: "30px 10px" }}>
              {task}
              <div style={{ fontSize: 40, color: colors.accent2, marginTop: 8 }}>→ AI ✔</div>
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
        社員は1人だけ
      </div>
    </Stage>
  );
};

const Shadow: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const frame = useCurrentFrame();
  const t = s.lines[1].from;
  const shake = frame < 20 ? Math.sin(frame * 2.2) * (20 - frame) * 0.8 : 0;
  return (
    <Stage>
      <Pop start={0}>
        <div style={{ fontSize: 60, fontWeight: 900, color: colors.danger }}>⚠️ でも、光と影</div>
      </Pop>
      <div style={{ translate: `${shake}px 0px`, width: "100%" }}>
        <Card style={{ textAlign: "center", borderColor: colors.danger, background: "rgba(255,59,92,0.15)" }}>
          <div style={{ fontSize: 48, fontWeight: 700, color: colors.muted }}>AI利用料がかさみ…（本人談）</div>
          <div style={{ fontSize: 112, fontWeight: 900, color: colors.danger, lineHeight: 1.1 }}>一部顧客で赤字</div>
        </Card>
      </div>
      <Pop start={t + 4}>
        <div style={{ fontSize: 70, color: colors.accent }}>↓</div>
      </Pop>
      <Pop start={t + 10} style={{ width: "100%" }}>
        <Card style={{ textAlign: "center", borderColor: colors.accent2 }}>
          <div style={{ fontSize: 60, fontWeight: 900 }}>
            <span style={{ color: colors.accent2 }}>無料</span>のオープンソースAIへ
          </div>
        </Card>
      </Pop>
    </Stage>
  );
};

const Outro: React.FC<{ s: SceneTiming }> = ({ s }) => {
  const frame = useCurrentFrame();
  const t = s.lines[1].from;
  const pressed = frame > t + 40 && frame < t + 52;
  const subscribed = frame >= t + 52;
  return (
    <Stage>
      <Pop start={2}>
        <div style={{ fontSize: 100, fontWeight: 900, color: colors.text, textAlign: "center", lineHeight: 1.3 }}>
          あなたなら
          <br />
          AIに<span style={{ color: colors.accent }}>何を任せる？</span>
        </div>
      </Pop>
      <Pop start={8}>
        <div style={{ fontSize: 48, fontWeight: 700, color: colors.muted }}>👇 コメントで教えてね</div>
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
            boxShadow: "0 10px 30px rgba(0,0,0,0.4)",
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
