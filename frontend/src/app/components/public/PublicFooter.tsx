import Link from "next/link";

export default function PublicFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-8 text-sm text-slate-700 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p className="text-slate-600">© {year} SOD Emuna Agency</p>
        <div className="flex flex-wrap items-center gap-4">
          <Link className="text-slate-700 transition hover:text-slate-900" href="https://t.me/sod_emuna_agency" target="_blank">
            Telegram
          </Link>
          <Link className="text-slate-700 transition hover:text-slate-900" href="https://wa.me/0000000000" target="_blank">
            WhatsApp
          </Link>
          <Link className="text-slate-700 transition hover:text-slate-900" href="/dashboard">
            Admin
          </Link>
        </div>
      </div>
    </footer>
  );
}
