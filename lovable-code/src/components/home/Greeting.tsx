function getGreeting() {
  const h = new Date().getHours();
  if (h < 6) return "Buenas noches";
  if (h < 13) return "Buenos dias";
  if (h < 20) return "Buenas tardes";
  return "Buenas noches";
}

export function Greeting() {
  return (
    <section>
      <h1 className="text-4xl sm:text-5xl font-bold">{getGreeting()}</h1>
      <p className="text-muted-foreground mt-2">Que te gustaria escuchar hoy?</p>
    </section>
  );
}
