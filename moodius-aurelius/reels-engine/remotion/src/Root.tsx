import React from 'react';
import {Composition, staticFile} from 'remotion';
import {Reel, ReelProps, FPS, LEAD_IN, TAIL} from './Reel';

// One composition renders any engine script: pass --props='{"script":"R001.json"}'.
export const Root: React.FC = () => (
  <Composition
    id="Reel"
    component={Reel}
    fps={FPS}
    width={1080}
    height={1920}
    durationInFrames={FPS}
    defaultProps={{script: 'R001.json', variant: 'a'} as ReelProps}
    calculateMetadata={async ({props}) => {
      const s = await fetch(staticFile(props.script)).then((r) => r.json());
      if (props.variant === 'b' && s.hook_b) s.cards[0][0] = s.hook_b;
      const total = s.cards.reduce((a: number, c: [string, number, string]) => a + c[1], 0);
      return {durationInFrames: Math.round((LEAD_IN + total + TAIL) * FPS), props: {...props, data: s}};
    }}
  />
);
