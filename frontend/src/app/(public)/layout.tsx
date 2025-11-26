import PublicFooter from "@/app/components/public/PublicFooter";
import PublicHeader from "@/app/components/public/PublicHeader";

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900">
      <PublicHeader />
      <main className="min-h-screen flex-1 bg-slate-50 text-slate-900">{children}</main>
      <PublicFooter />
    </div>
  );
}
