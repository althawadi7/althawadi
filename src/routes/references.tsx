import { createFileRoute } from "@tanstack/react-router";
import { PageHero } from "@/components/PageHero";
import { ExternalLink } from "lucide-react";

export const Route = createFileRoute("/references")({
  head: () => ({
    meta: [
      { title: "مراجع ومصادر عن عائلة الذوادي" },
      { name: "description", content: "مقالات ومواقع ومصادر خارجية تتحدث عن عائلة الذوادي وتاريخها." },
      { property: "og:title", content: "مراجع عائلة الذوادي" },
      { property: "og:description", content: "مصادر ومقالات خارجية عن عائلة الذوادي." },
      { property: "og:url", content: "/references" },
    ],
    links: [{ rel: "canonical", href: "/references" }],
  }),
  component: ReferencesPage,
});

const references = [
  {
    title: "حساب مجلس الذوادي على إنستغرام",
    description: "حسابنا الرسمي الذي نشارك فيه آخر أخبار المجلس ومناسبات العائلة.",
    url: "https://www.instagram.com/althawadi_majlis/?hl=ar",
  },
  // أضف هنا مراجع إضافية:
  // {
  //   title: "عنوان المقالة أو المصدر",
  //   description: "وصف مختصر",
  //   url: "https://example.com/article",
  // },
];

function ReferencesPage() {
  return (
    <>
      <PageHero
        eyebrow="References — مراجع ومصادر"
        title="مصادرنا ومراجعنا"
        description="مقالات ومواقع ومصادر خارجية تتحدث عن عائلة الذوادي. نستمر في إثراء هذه الصفحة بكلّ ما يُكتب عن بيتنا ومجلسنا."
      />

      <section className="mx-auto max-w-4xl px-6 py-20">
        {references.length > 0 ? (
          <ul className="space-y-6">
            {references.map((ref, i) => (
              <li key={i}>
                <a
                  href={ref.url}
                  target="_blank"
                  rel="noreferrer"
                  className="group block border border-border rounded-sm p-6 bg-card/40 hover:bg-card transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="font-display text-xl text-foreground group-hover:text-accent transition-colors">
                        {ref.title}
                      </h3>
                      <p className="mt-2 text-sm text-muted-foreground leading-7">
                        {ref.description}
                      </p>
                      <span className="mt-3 inline-block text-xs text-primary font-latin break-all">
                        {ref.url}
                      </span>
                    </div>
                    <ExternalLink className="h-5 w-5 text-muted-foreground group-hover:text-accent transition-colors shrink-0 mt-1" strokeWidth={1.4} />
                  </div>
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-center border border-border rounded-sm p-12 bg-card/40">
            <p className="text-muted-foreground leading-8">
              سيتمّ إضافة المراجع والمصادر قريبًا.
            </p>
          </div>
        )}

        <div className="mt-16 border-t border-border pt-10 text-center">
          <p className="text-sm text-muted-foreground leading-8 max-w-xl mx-auto">
            هل تعرف مقالة أو مصدرًا يتحدث عن عائلة الذوادي؟
            <a href="/contact" className="text-accent hover:underline mr-1">تواصل معنا</a>
            لإضافته هنا.
          </p>
        </div>
      </section>
    </>
  );
}
