"use client";

import CommandForm from "@/app/components/dashboard/command-form";

export default function CommandsPage() {
  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <h2 className="text-2xl font-semibold text-white">Commands</h2>
        <p className="text-sm text-slate-300">Trigger manual missions and inspect their status.</p>
      </div>
      <CommandForm />
    </div>
  );
}
