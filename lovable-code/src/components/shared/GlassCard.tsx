interface Props {
  children: React.ReactNode;
  className?: string;
  as?: "section" | "div";
}

export function GlassCard({ children, className = "", as: Tag = "section" }: Props) {
  return <Tag className={`glass rounded-2xl p-5 sm:p-6 ${className}`}>{children}</Tag>;
}
