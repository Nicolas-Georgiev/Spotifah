import { createContext, useContext, useState, type ReactNode } from "react";
import type { ConvItem } from "../components/convert/ConversionItem";

interface ConvertData {
  activeImportTaskId: string | null;
  completedPlaylistId: number | null;
  items: ConvItem[];
  setActiveImportTaskId: (id: string | null) => void;
  setCompletedPlaylistId: (id: number | null) => void;
  setItems: React.Dispatch<React.SetStateAction<ConvItem[]>>;
}

const ConvertDataContext = createContext<ConvertData | null>(null);

export function useConvertData() {
  const ctx = useContext(ConvertDataContext);
  if (!ctx) throw new Error("useConvertData must be used within ConvertDataProvider");
  return ctx;
}

interface Props {
  children: ReactNode;
}

export function ConvertDataProvider({ children }: Props) {
  const [activeImportTaskId, setActiveImportTaskId] = useState<string | null>(null);
  const [completedPlaylistId, setCompletedPlaylistId] = useState<number | null>(null);
  const [items, setItems] = useState<ConvItem[]>([]);

  return (
    <ConvertDataContext.Provider
      value={{
        activeImportTaskId,
        completedPlaylistId,
        items,
        setActiveImportTaskId,
        setCompletedPlaylistId,
        setItems,
      }}
    >
      {children}
    </ConvertDataContext.Provider>
  );
}
