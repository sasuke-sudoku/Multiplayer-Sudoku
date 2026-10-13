import { Audio } from "@remotion/media";
import { useEffect, useState } from "react";
import { AbsoluteFill, Composition, continueRender, delayRender, Sequence, staticFile } from "remotion";
import { Background, Caption, Header } from "./parts";
import { sceneComponents } from "./Scenes";
import { FPS, fontFamily, HEIGHT, lines, sceneDefs, scenes, totalFrames, WIDTH } from "./theme";

export const MyComposition = () => {
  return (
    <Composition
      id="TrendShort"
      component={TrendShort}
      durationInFrames={totalFrames}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};

export const TrendShort: React.FC = () => {
  // Font subsets load lazily per glyph range; hold the frame until they have arrived.
  const [handle] = useState(() => delayRender("Loading fonts"));
  useEffect(() => {
    requestAnimationFrame(() => {
      document.fonts.ready.then(() => continueRender(handle));
    });
  }, [handle]);

  return (
    <AbsoluteFill style={{ fontFamily }}>
      <Background />
      {scenes.map((s, i) => {
        const def = sceneDefs.find((d) => d.id === s.id);
        if (!def) throw new Error(`No scene "${s.id}" in episode.scenes`);
        const Scene = sceneComponents[def.type] as React.FC<{ s: typeof s; d: typeof def.data }>;
        if (!Scene) throw new Error(`Unknown scene type "${def.type}"`);
        return (
          <Sequence key={i} name={`Scene: ${s.id} (${def.type})`} from={s.from} durationInFrames={s.duration}>
            <Scene s={s} d={def.data} />
          </Sequence>
        );
      })}
      <Header />
      {lines.map((line, i) => (
        <Sequence key={i} name={`Line ${i + 1}`} from={line.from} durationInFrames={line.duration}>
          <Audio src={staticFile(line.file)} />
          <Caption line={line} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
