import { Audio } from "@remotion/media";
import { useEffect, useState } from "react";
import { AbsoluteFill, Composition, continueRender, delayRender, Sequence, staticFile } from "remotion";
import { Background, Caption, Header } from "./parts";
import { sceneComponents } from "./Scenes";
import { FPS, fontFamily, HEIGHT, lines, scenes, totalFrames, WIDTH } from "./theme";

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
      {scenes.map((s) => {
        const Scene = sceneComponents[s.id];
        return (
          <Sequence key={s.id} name={`Scene: ${s.id}`} from={s.from} durationInFrames={s.duration}>
            <Scene s={s} />
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
