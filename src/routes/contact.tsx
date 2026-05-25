import { createFileRoute } from "@tanstack/react-router";
import { PageHero } from "@/components/PageHero";
import { Instagram, Mail, MessageCircle } from "lucide-react";

export const Route = createFileRoute("/contact")({
  head: () => ({
    meta: [
      { title: "تواصل مع مجلس الذوادي" },
      { name: "description", content: "للتواصل مع مجلس عائلة الذوادي والمساهمة بالمعلومات والصور." },
      { property: "og:title", content: "تواصل مع الذوادي" },
      { property: "og:url", content: "/contact" },
    ],
    links: [{ rel: "canonical", href: "/contact" }],
  }),
  component: ContactPage,
});

function ContactPage() {
  return (
    <>
      <PageHero
        eyebrow="Contact — تواصل معنا"
        title="بابُ المجلسِ مفتوح"
        description="نرحّب بكلّ أبناء العائلة وأصدقائها. شاركونا الصور، الذكريات، أو معلوماتٍ تثري هذا الأرشيف."
      />

      <section className="mx-auto max-w-5xl px-6 py-20 grid gap-10 md:grid-cols-2">
        <div className="space-y-6">
          <a
            href="https://www.instagram.com/althawadi_majlis/?hl=ar"
            target="_blank"
            rel="noreferrer"
            className="flex items-start gap-4 border border-border rounded-sm p-6 bg-card/50 hover:bg-card transition-colors"
          >
            <Instagram className="h-6 w-6 text-accent mt-1" strokeWidth={1.4} />
            <div>
              <div className="font-display text-xl text-foreground">إنستغرام</div>
              <div className="text-sm text-muted-foreground mt-1 font-latin">@althawadi_majlis</div>
              <p className="text-sm text-muted-foreground mt-2 leading-7">
                للراسلة المباشرة ومتابعة آخر أخبار المجلس.
              </p>
            </div>
          </a>

          <div className="flex items-start gap-4 border border-border rounded-sm p-6">
            <MessageCircle className="h-6 w-6 text-accent mt-1" strokeWidth={1.4} />
            <div>
              <div className="font-display text-xl text-foreground">مجلس العائلة</div>
              <p className="text-sm text-muted-foreground mt-2 leading-7">
                للحضور إلى المجلس أو التنسيق لزيارة، يُرجى التواصل عبر إنستغرام
                أو النموذج المجاور.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 border border-border rounded-sm p-6">
            <Mail className="h-6 w-6 text-accent mt-1" strokeWidth={1.4} />
            <div>
              <div className="font-display text-xl text-foreground">بريد إلكتروني</div>
              <p className="text-sm text-muted-foreground mt-2 leading-7">
                سيتمّ إضافة بريد رسمي للمجلس قريبًا.
              </p>
            </div>
          </div>
        </div>

        <form
          className="border border-border rounded-sm p-8 bg-card/40 space-y-5"
          onSubmit={(e) => {
            e.preventDefault();
            alert("شكرًا لتواصلكم. سيتمّ الرّد عليكم قريبًا إن شاء الله.");
          }}
        >
          <div>
            <label className="block text-sm mb-2">الاسم الكامل</label>
            <input
              required
              type="text"
              className="w-full rounded-sm border border-input bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="اكتب اسمك"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">طريقة التواصل</label>
            <input
              type="text"
              className="w-full rounded-sm border border-input bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="هاتف أو بريد إلكتروني"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">رسالتك</label>
            <textarea
              required
              rows={5}
              className="w-full rounded-sm border border-input bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="معلومات، صور، أو ملاحظات تودّ مشاركتها..."
            />
          </div>
          <button
            type="submit"
            className="w-full rounded-sm bg-primary px-5 py-3 text-sm text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            إرسال
          </button>
        </form>
      </section>
    </>
  );
}
