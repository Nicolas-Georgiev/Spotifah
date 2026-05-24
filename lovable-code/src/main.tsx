import "./styles.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "@tanstack/react-router";
import { router } from "./router";
import { AppDataProvider } from "./lib/app-data";
import { ConvertDataProvider } from "./lib/convert-data";
import { ThemeProvider } from "./lib/theme-provider";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <AppDataProvider>
        <ConvertDataProvider>
          <RouterProvider router={router} />
        </ConvertDataProvider>
      </AppDataProvider>
    </ThemeProvider>
  </StrictMode>,
);
