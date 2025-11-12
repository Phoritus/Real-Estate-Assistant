import React from 'react';

interface LoadingIconProps {
  size?: number;
  color?: string;
  className?: string;
  title?: string;
}

// Reusable animated loading icon based on provided SVG.
// Uses currentColor so you can wrap it in a parent with color set (e.g., color="inherit").
export const LoadingIcon: React.FC<LoadingIconProps> = ({ size = 24, color = 'currentColor', className, title }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    role="img"
    aria-label={title || 'Loading'}
    className={className}
    style={{ display: 'inline-block', verticalAlign: 'middle', color }}
  >
    {title && <title>{title}</title>}
    <defs>
      <filter id="spinnerBlur"><feGaussianBlur in="SourceGraphic" result="y" stdDeviation="1.5"/><feColorMatrix in="y" result="z" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 18 -7"/><feBlend in="SourceGraphic" in2="z"/></filter>
    </defs>
    <g fill="currentColor" filter="url(#spinnerBlur)">
      <circle cx="4" cy="12" r="3">
        <animate attributeName="cx" calcMode="spline" dur="0.75s" keySplines=".56,.52,.17,.98;.56,.52,.17,.98" repeatCount="indefinite" values="4;9;4" />
        <animate attributeName="r" calcMode="spline" dur="0.75s" keySplines=".56,.52,.17,.98;.56,.52,.17,.98" repeatCount="indefinite" values="3;8;3" />
      </circle>
      <circle cx="15" cy="12" r="8">
        <animate attributeName="cx" calcMode="spline" dur="0.75s" keySplines=".56,.52,.17,.98;.56,.52,.17,.98" repeatCount="indefinite" values="15;20;15" />
        <animate attributeName="r" calcMode="spline" dur="0.75s" keySplines=".56,.52,.17,.98;.56,.52,.17,.98" repeatCount="indefinite" values="8;3;8" />
      </circle>
    </g>
  </svg>
);

export default LoadingIcon;