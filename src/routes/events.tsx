import { createFileRoute } from "@tanstack/react-router";
import { PageHero } from "@/components/PageHero";

export const Route = createFileRoute("/events")({
  head: () => ({
    meta: [
      { title: "مناسبات عائلة آل الذوادي" },
      { name: "description", content: "تقويم مناسبات وتجمعات عائلة آل الذوادي." },
      { property: "og:title", content: "مناسبات آل الذوادي" },
      { property: "og:url", content: "/events" },
    ],
    links: [{ rel: "canonical", href: "/events" }],
  }),
  component: EventsPage,
});

const events = [
  { date: "—", month: "رمضان", title: "غبقة العائلة السنويّة", place: "مجلس آل الذوادي" },
  { date: "—", month: "شوال", title: "تجمّع العيد", place: "بيت الجد" },
  { date: "—", month: "ذو الحجة", title: "لقاء الأبناء والأحفاد", place: "المجلس الكبير" },
  { date: "—", month: "محرم", title: "اجتماع تنسيق المجلس", place: "المجلس" },
];

function EventsPage() {
  return (
    <>
      <PageHero
        eyebrow="Events — المناسبات"
        title="تقويمُ مجلسنا"
        description="مناسبات نتطلّع إليها سويًّا، ومواعيد نتذكّرها لنحفظ روابط الرحم."
      />

      <section className="mx-auto max-w-4xl px-6 py-20">
        <ul className="divide-y divide-border border border-border rounded-sm overflow-hidden bg-card/40">
          {events.map((e, i) => (
            <li key={i} className="grid grid-cols-[auto_1fr_auto] items-center gap-6 p-6 hover:bg-card transition-colors">
              <div className="text-center w-20 border-l border-border pl-6">
                <div className="font-display text-3xl text-accent">{e.date}</div>
                <div className="text-[10px] uppercase tracking-widest text-muted-foreground mt-1">{e.month}</div>
              </div>
              <div>
                <div className="font-display text-xl text-foreground">{e.title}</div>
                <div className="text-sm text-muted-foreground mt-1">{e.place}</div>
              </div>
              <span className="text-xs text-muted-foreground hidden sm:inline">قريبًا</span>
            </li>
          ))}
        </ul>

        <p className="mt-10 text-center text-sm text-muted-foreground">
          سيتمّ تحديث التواريخ بمجرّد اعتمادها من مجلس العائلة.
        </p>
      </section>
    </>
  );
}
