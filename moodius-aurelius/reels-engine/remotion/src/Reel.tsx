import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// Phase 1 tokens (same values as tools/design.py). Flat grounds, one Ember accent, no gradients.
export const SLATE = '#1B1F24', BONE = '#F3EFE7', ASH = '#B8B3A9', EMBER = '#C9742E';
export const FPS = 30, LEAD_IN = 0.2, TAIL = 0.2, MARGIN = 96;
type Card = [string, number, 'hook' | 'body' | 'quote' | 'cite' | 'cta'];
export type ReelProps = {script: string; variant?: 'a' | 'b'; data?: {id: string; cards: Card[]; audio: {mood: string}}};

const fonts = `
@font-face{font-family:Playfair;font-weight:600;src:url(${staticFile('fonts/Playfair-SemiBold.ttf')})}
@font-face{font-family:Playfair;font-style:italic;font-weight:500;src:url(${staticFile('fonts/Playfair-MediumItalic.ttf')})}
@font-face{font-family:Inter;font-weight:400;src:url(${staticFile('fonts/Inter-Regular.otf')})}
@font-face{font-family:Inter;font-weight:500;src:url(${staticFile('fonts/Inter-Medium.otf')})}
@font-face{font-family:Inter;font-weight:600;src:url(${staticFile('fonts/Inter-SemiBold.otf')})}`;

const STYLE: Record<Card[2], React.CSSProperties> = {
  hook: {fontFamily: 'Playfair', fontWeight: 600, fontSize: 84, color: BONE, lineHeight: 1.18},
  quote: {fontFamily: 'Playfair', fontStyle: 'italic', fontWeight: 500, fontSize: 64, color: BONE, lineHeight: 1.28},
  body: {fontFamily: 'Inter', fontWeight: 500, fontSize: 60, color: BONE, lineHeight: 1.28},
  cite: {fontFamily: 'Inter', fontWeight: 500, fontSize: 32, color: ASH, letterSpacing: 2, textTransform: 'uppercase'},
  cta: {fontFamily: 'Inter', fontWeight: 600, fontSize: 50, color: BONE, lineHeight: 1.28},
};

// Words arrive one after another (hook, quote) or as one line (others); the card fades out as a unit.
const CardView: React.FC<{text: string; kind: Card[2]; dur: number}> = ({text, kind, dur}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const out = interpolate(frame, [(dur - 0.3) * fps, dur * fps], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const words = text.split(' ');
  const stagger = kind === 'quote' ? Math.min(3, (dur * 0.45 * fps) / words.length) : kind === 'hook' ? 2.2 : 0;
  const rule = spring({frame: frame - 0.35 * fps, fps, config: {damping: 200}});
  return (
    <AbsoluteFill style={{padding: `0 ${MARGIN}px`, justifyContent: 'center', top: -80, opacity: out}}>
      <div style={{...STYLE[kind], textWrap: 'balance' as any}}>
        {words.map((w, i) => {
          const p = spring({frame: frame - i * stagger, fps, config: {damping: 200}, durationInFrames: 12});
          return (
            <span key={i} style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * 14}px)`, whiteSpace: 'pre'}}>
              {w + (i < words.length - 1 ? ' ' : '')}
            </span>
          );
        })}
      </div>
      {kind === 'hook' && <div style={{marginTop: 26, height: 5, width: 120 * rule, background: EMBER}} />}
    </AbsoluteFill>
  );
};

// Thin Ember progress line along the bottom safe margin: viewers see how short the reel is.
const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  return <div style={{position: 'absolute', left: MARGIN, bottom: 300, height: 3, width: (1080 - 2 * MARGIN) * (frame / durationInFrames), background: EMBER, opacity: 0.55}} />;
};

export const Reel: React.FC<ReelProps> = ({data}) => {
  const {fps} = useVideoConfig();
  if (!data) return null;
  let t = LEAD_IN;
  return (
    <AbsoluteFill style={{background: SLATE}}>
      <style>{fonts}</style>
      <div style={{position: 'absolute', left: MARGIN, top: MARGIN + 190, display: 'flex', alignItems: 'center', gap: 16}}>
        <div style={{width: 14, height: 14, background: EMBER}} />
        <div style={{fontFamily: 'Inter', fontWeight: 600, fontSize: 28, color: BONE, letterSpacing: 9}}>MOODIUS</div>
      </div>
      {data.cards.map(([text, dur, kind], i) => {
        const from = Math.round(t * fps);
        t += dur;
        return (
          <Sequence key={i} from={from} durationInFrames={Math.round(dur * fps)} layout="none">
            <CardView text={kind === 'cite' ? text : text} kind={kind} dur={dur} />
          </Sequence>
        );
      })}
      <div style={{position: 'absolute', left: MARGIN, top: 1560, fontFamily: 'Inter', fontSize: 32, color: ASH}}>@moodiusaurelius</div>
      <Progress />
      <Audio src={staticFile(`${data.id}-bed.wav`)} />
    </AbsoluteFill>
  );
};
