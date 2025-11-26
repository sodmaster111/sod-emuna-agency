import type { Metadata } from "next";

import CommandCenterPage from "./command-center-client";

export const metadata: Metadata = {
  title: "Home",
};

export default function HomePage() {
  return <CommandCenterPage />;
}
