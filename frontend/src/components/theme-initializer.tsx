"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

import { applyThemeVariables, DEFAULT_THEME, fetchThemePalette } from "@/lib/theme";

export function ThemeInitializer() {
  const { data } = useQuery({
    queryKey: ["theme"],
    queryFn: fetchThemePalette,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    applyThemeVariables(data ?? DEFAULT_THEME);
  }, [data]);

  return null;
}
