import { createFileRoute } from "@tanstack/react-router";
import { PageHero } from "@/components/PageHero";

export const Route = createFileRoute("/ancestors")({
  head: () => ({
    meta: [
      { title: "أجداد عائلة الذوادي" },
      { name: "description", content: "سير الأجداد والشخصيات البارزة في عائلة الذوادي." },
      { property: "og:title", content: "أجداد عائلة الذوادي" },
      { property: "og:url", content: "/ancestors" },
    ],
    links: [{ rel: "canonical", href: "/ancestors" }],
  }),
  component: AncestorsPage,
});

const ancestors = [
  {
    name: "الجدّ المؤسّس",
    title: "مؤسّس بيت الذوادي",
    years: "— — —",
    bio: "أوّل من حمل الاسم وأرسى قواعد البيت. عُرف بكرمه ومجلسه المفتوح، وكان حكيمًا في الفصل بين الناس.",
  },
  {
    name: "الجدّ الأول",
    title: "حافظُ الإرث",
    years: "— — —",
    bio: "تابع مسيرة أبيه وعمل على توسعة المجلس، وكان من أهل الرأي والمشورة في قبيلته.",
  },
  {
    name: "الجدّ الثاني",
    title: "رجلُ المروءة",
    years: "— — —",
    bio: "اشتهر بمساعدة المحتاجين، ووقف إلى جانب أهله في السرّاء والضرّاء، فأصبح اسمه مضرب المثل في الكرم.",
  },
  {
    name: "الجدّ الثالث",
    title: "صاحبُ العلم والأدب",
    years: "— — —",
    bio: "اعتنى بتعليم أبنائه، وكان شغوفًا بالشعر والأدب، حفظ منه الكثير ورواه لأبنائه.",
  },
];

function AncestorsPage() {
  return (
    <>
      <PageHero
        eyebrow="Ancestors — سير الأجداد"
        title="رجالٌ صنعوا الاسم"
        description="نستذكر هنا من أرسوا قواعد البيت، ونحفظ لهم الفضل والذكر الطيّب. كل اسمٍ منهم حكاية، وكل حكاية درسٌ للأجيال."
      />

      <section className="mx-auto max-w-5xl px-6 py-20">
        <ol className="relative border-r border-border pr-8 md:pr-12 space-y-16">
          {ancestors.map((a, i) => (
            <li key={a.name} className="relative">
              <span className="absolute -right-[42px] md:-right-[54px] top-1 grid h-10 w-10 place-items-center rounded-full bg-background border border-accent text-accent font-display">
                {["١", "٢", "٣", "٤"][i]}
              </span>
              <p className="text-[11px] uppercase tracking-[0.3em] text-accent font-latin">{a.years}</p>
              <h3 className="mt-2 font-display text-3xl text-foreground">{a.name}</h3>
              <p className="mt-1 text-primary italic">{a.title}</p>
              <p className="mt-4 text-muted-foreground leading-9">{a.bio}</p>
            </li>
          ))}
        </ol>

        <div className="mt-20 text-center text-sm text-muted-foreground border-t border-border pt-10">
          نُحدّث هذه الصفحة باستمرار. لإضافة سيرة جدٍّ أو شخصيّة بارزة من العائلة،
          تواصلوا معنا.
        </div>
      </section>
    </>
  );
}
