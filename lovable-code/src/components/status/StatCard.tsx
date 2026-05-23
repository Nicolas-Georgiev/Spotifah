interface Props {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  description: string;
}

export function StatCard({ icon, label, value, description }: Props) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        {icon}
        <span>{label}</span>
      </div>
      <p className="text-3xl font-semibold mt-4">{value}</p>
      <p className="text-xs text-muted-foreground mt-3">{description}</p>
    </div>
  );
}
