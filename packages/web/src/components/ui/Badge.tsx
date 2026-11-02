import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'danger' | 'warning' | 'safe' | 'neutral';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  className = '',
  ...props
}) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
  }[size];

  const variantClasses = {
    danger: 'badge-phishing font-bold',
    warning: 'badge-warning font-semibold',
    safe: 'badge-legit font-semibold',
    neutral: 'app-card-subtle app-text-secondary border app-border font-mono',
  }[variant];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded font-mono uppercase tracking-wider select-none ${sizeClasses} ${variantClasses} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};
