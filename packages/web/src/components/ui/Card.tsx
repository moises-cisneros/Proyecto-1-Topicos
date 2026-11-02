import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'subtle' | 'threat' | 'safe';
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  className = '',
  ...props
}) => {
  const variantClasses = {
    default: 'app-card border rounded-xl',
    subtle: 'app-card-subtle border rounded-lg',
    threat: 'app-card border-2 border-[#ef233c] rounded-xl',
    safe: 'app-card border-2 border-[#8d99ae] rounded-xl',
  }[variant];

  return (
    <div className={`${variantClasses} ${className}`} {...props}>
      {children}
    </div>
  );
};
