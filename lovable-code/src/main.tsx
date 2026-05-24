import "./styles.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "@tanstack/react-router";
import { router } from "./router";
import { AppDataProvider } from "./lib/app-data";
import { ConvertDataProvider } from "./lib/convert-data";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppDataProvider>
      <ConvertDataProvider>
        <RouterProvider router={router} />
      </ConvertDataProvider>
    </AppDataProvider>
  </StrictMode>,
);
