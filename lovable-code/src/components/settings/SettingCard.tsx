interface Props {
  icon: React.ReactNode;
  iconBg: string;
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

export function SettingCard({ icon, iconBg, title, subtitle, children }: Props) {
  return (
    <section className="glass rounded-2xl p-5 sm:p-6">
      <div className="flex items-start gap-4">
        <div className={`w-11 h-11 rounded-xl grid place-items-center shrink-0 ${iconBg}`}>{icon}</div>
        <div className="flex-1">
          <h2 className="text-lg font-semibold">{title}</h2>
          <p className="text-sm text-muted-foreground mt-0.5">{subtitle}</p>
          <div className="mt-4">{children}</div>
        </div>
      </div>
    </section>
  );
}
