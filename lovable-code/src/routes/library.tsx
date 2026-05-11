import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/library")({
  head: () => ({ meta: [{ title: "Biblioteca — EKHO" }] }),
  component: () => <Outlet />,
});
