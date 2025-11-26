import Link from "next/link";

const navItems = [
  { label: "Home", href: "/" },
  { label: "Join", href: "/join" },
  { label: "Login", href: "/login" },
];

export function PublicHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link className="text-lg font-semibold tracking-tight text-white" href="/">
          SOD Autonomous Agency
        </Link>

        <nav className="flex items-center gap-2 text-sm text-slate-200">
          {navItems.map((item) => (
            <Link
              key={item.href}
              className="rounded-lg px-3 py-2 transition hover:bg-white/5"
              href={item.href}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

export default PublicHeader;
