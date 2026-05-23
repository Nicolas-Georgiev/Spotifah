interface Props {
  src?: string;
  alt?: string;
  className?: string;
  icon?: string;
}

export function CoverArt({ src, alt = "", className = "text-4xl", icon = "♪" }: Props) {
  if (src) {
    return <img src={src} alt={alt} className={className} />;
  }
  return <span className={className}>{icon}</span>;
}
