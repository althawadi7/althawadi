import { createFileRoute } from "@tanstack/react-router";
import { PageHero } from "@/components/PageHero";
import { Instagram, ExternalLink } from "lucide-react";

export const Route = createFileRoute("/news")({
  head: () => ({
    meta: [
      { title: "أخبار مجلس آل الذوادي" },
      { name: "description", content: "آخر أخبار وأنشطة مجلس عائلة آل الذوادي عبر إنستغرام." },
      { property: "og:title", content: "أخبار مجلس آل الذوادي" },
      { property: "og:url", content: "/news" },
    ],
    links: [{ rel: "canonical", href: "/news" }],
  }),
  component: NewsPage,
});

function NewsPage() {
  return (
    <>
      <PageHero
        eyebrow="News — أخبار المجلس"
        title="ما يجري في مجلسنا"
        description="نشاركُ آخر أنشطة المجلس وتجمعات العائلة عبر حساب إنستغرام الرسمي."
      />

      <section className="mx-auto max-w-3xl px-6 py-20 text-center">
        <div className="border border-border rounded-sm p-12 bg-card/60 paper-texture">
          <Instagram className="mx-auto h-10 w-10 text-accent" strokeWidth={1.2} />
          <h2 className="mt-6 font-display text-3xl text-foreground">مجلس آل الذوادي على إنستغرام</h2>
          <p className="mt-4 text-muted-foreground leading-8">
            تابعوا حسابنا الرسمي لمتابعة آخر الصور، الإعلانات، ومناسبات العائلة.
            ندعوكم للمشاركة معنا والتفاعل.
          </p>
          <a
            href="https://www.instagram.com/althawadi_majlis/?hl=ar"
            target="_blank"
            rel="noreferrer"
            className="mt-8 inline-flex items-center gap-3 rounded-sm bg-primary px-7 py-3 text-sm text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            <span className="font-latin tracking-wider">@althawadi_majlis</span>
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>

        <p className="mt-10 text-sm text-muted-foreground">
          قريبًا — سنضيف هنا أرشيفًا منظّمًا للإعلانات والأخبار العائليّة.
        </p>
      </section>
    </>
  );
}
