import { useEffect, useRef } from 'react';

/**
 * Circular score visualization matching the DevMutDB design.
 *
 * Color coding:
 *   ≥ 20  →  red    (critical developmental impact)
 *   9-19  →  orange (moderate developmental impact)
 *   < 9   →  green  (limited developmental impact)
 *
 * Animates the ring stroke on mount using requestAnimationFrame.
 */
export default function ScoreRing({ score, size = 130 }) {
  const circleRef = useRef(null);
  const radius = size * 0.38;
  const strokeWidth = size * 0.06;
  const circumference = 2 * Math.PI * radius;
  const center = size / 2;

  // Color based on score tier
  const danger = '#E74C3C'; // Critical red
  const moderate = '#F39C12'; // Moderate orange
  const low = '#27AE60'; // Low green
  const color = score >= 20 ? danger : score >= 9 ? moderate : low;

  useEffect(() => {
    const circle = circleRef.current;
    if (!circle) return;

    // Start fully hidden, animate to correct offset
    const targetOffset = circumference - (score / 100) * circumference;
    circle.style.strokeDashoffset = circumference;

    // Trigger animation after paint
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        circle.style.transition = 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        circle.style.strokeDashoffset = targetOffset;
      });
    });
  }, [score, circumference]);

  return (
    <div className="score-ring-wrapper" id="score-ring">
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        aria-label={`DevScore: ${Math.round(score)}`}
      >
        {/* Background circle */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          ref={circleRef}
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          strokeLinecap="round"
          transform={`rotate(-90 ${center} ${center})`}
        />
        {/* Score number */}
        <text
          x={center}
          y={center + size * 0.02}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={size * 0.28}
          fontWeight="700"
          fontFamily="'Inter', sans-serif"
          fill={color}
        >
          {Math.round(score)}
        </text>
      </svg>
      <span className="score-ring-label">DevScore</span>
    </div>
  );
}