export default function ContactPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-slate-900">צור קשר</h1>
      <p className="text-lg text-slate-700">
        נשמח לשמוע מכם. ניתן לפנות אלינו בכל שאלה, בקשה או הצעה דרך הערוצים הבאים.
      </p>
      <div className="space-y-3 rounded-2xl border border-slate-200 bg-white/80 p-6 shadow-sm shadow-slate-200/60">
        <div>
          <p className="text-sm font-semibold text-slate-900">Email</p>
          <p className="text-sm text-slate-700">contact@sod-emuna.agency</p>
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900">Telegram</p>
          <p className="text-sm text-slate-700">@sod_emuna_agency</p>
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900">WhatsApp</p>
          <p className="text-sm text-slate-700">+972-00-000-0000</p>
        </div>
      </div>
    </div>
  );
}
