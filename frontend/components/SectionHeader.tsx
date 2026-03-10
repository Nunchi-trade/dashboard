import React from "react";

interface SectionHeaderProps {
  badge: string;
  title: string;
  description: string;
}

export default function SectionHeader({ badge, title, description }: SectionHeaderProps) {
  return (
    <div className="flex flex-col gap-1">
      <p className="text-xs font-semibold uppercase tracking-[0.6px] text-dark leading-4">
        {badge}
      </p>
      <h2 className="text-[38px] font-normal text-dark leading-[47.5px] font-serif">
        {title}
      </h2>
      <p className="text-xs text-desc leading-[19.5px] max-w-[768px]">
        {description}
      </p>
    </div>
  );
}
