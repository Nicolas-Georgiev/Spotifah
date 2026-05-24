import { createFileRoute } from "@tanstack/react-router";
import { RecommendationsPage } from "../components/recommendations/RecommendationsPage";

export const Route = createFileRoute("/recommendations")({
  head: () => ({ meta: [{ title: "Recomendaciones — EKHO" }] }),
  component: RecommendationsPage,
});
