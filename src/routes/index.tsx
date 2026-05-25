import { createFileRoute, Link } from "@tanstack/react-router";
import heroImage from "@/assets/hero-majlis.jpg";
import heritageImage from "@/assets/heritage.jpg";
import palmImage from "@/assets/palm.jpg";
import { ArrowLeft, Users, BookOpen, Image as ImageIcon, Calendar } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "الذوادي — مجلس العائلة" },
      { name: "description", content: "بيت من الذكريات، وصفحة من التاريخ. تعرّف على عائلة الذوادي، شجرتها، أجدادها وأخبار مجلسها." },
      { property: "og:title", content: "الذوادي — مجلس العائلة" },
      { property: "og:description", content: "تاريخ ونسب وذكريات عائلة الذوادي." },
      { property: "og:url", content: "/" },
    ],
    links: [{ rel: "canonical", href: "/" }],
  }),
  component: HomePage,
});

function HomePage() {
  return (
    <>
      {/* HERO */}
      <section className="relative overflow-hidden border-b border-border">
        <div className="absolute inset-0">
          <img
            src={heroImage}
            alt="مجلس عائلة الذوادي"
            width={1920}
            height={1280}
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-l from-background via-background/70 to-background/20" />
        </div>

        <div className="relative mx-auto max-w-7xl px-6 py-28 md:py-40">
          <div className="max-w-2xl">
            <p className="text-xs uppercase tracking-[0.5em] text-accent font-latin">EST. تاريخ عريق</p>
            <div className="ornament my-6 w-44" />
            <h1 className="font-display text-5xl md:text-7xl text-foreground leading-tight">
              آلُ الذَّوادي
              <span className="block text-3xl md:text-4xl text-primary/80 mt-3">عائلةٌ، تاريخٌ، وذاكرة</span>
            </h1>
            <p className="mt-8 text-lg text-muted-foreground leading-9 max-w-xl">
              في هذا الموقع نجمع شتات الذكرى، ونحفظ ما تركه الأجداد من سيرة طيّبة،
              ونوثّق نسبنا وصورنا، ليبقى الإرث حاضرًا في قلوب الأبناء والأحفاد.
            </p>

            <div className="mt-10 flex flex-wrap gap-3">
              <Link
                to="/tree"
                className="inline-flex items-center gap-2 rounded-sm bg-primary px-6 py-3 text-sm text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                <span>اكتشف شجرة العائلة</span>
                <ArrowLeft className="h-4 w-4" />
              </Link>
              <Link
                to="/about"
                className="inline-flex items-center gap-2 rounded-sm border border-border bg-background/60 px-6 py-3 text-sm hover:bg-card transition-colors"
              >
                عن العائلة
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* INTRO QUOTE */}
      <section className="border-b border-border bg-card/30 paper-texture">
        <div className="mx-auto max-w-4xl px-6 py-20 text-center">
          <div className="ornament mx-auto w-32 mb-8" />
          <p className="font-display text-2xl md:text-3xl text-foreground leading-relaxed">
            «من لم يعرف ماضيه، ضاع حاضره، وغاب عنه مستقبله.»
          </p>
          <p className="mt-6 text-sm text-muted-foreground tracking-wider">— حكمة الأجداد</p>
        </div>
      </section>

      {/* PILLARS */}
      <section className="mx-auto max-w-7xl px-6 py-24">
        <div className="text-center mb-16">
          <p className="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">ما يجمعنا</p>
          <h2 className="mt-3 font-display text-4xl text-foreground">أربعةُ أركانٍ لذاكرتنا</h2>
        </div>

        <div className="grid gap-px bg-border md:grid-cols-2 lg:grid-cols-4 border border-border">
          {[
            { icon: Users, title: "شجرة العائلة", text: "أنسابنا الموثّقة جيلًا بعد جيل، من الجد الأكبر إلى أصغر الأحفاد.", to: "/tree" },
            { icon: BookOpen, title: "سير الأجداد", text: "حكايات الرجال الذين أسّسوا اسم الذوادي ورسموا مجده.", to: "/ancestors" },
            { icon: ImageIcon, title: "معرض الصور", text: "صور أرشيفية وعائلية تختزن لحظات لا تُنسى من زمنٍ مضى.", to: "/gallery" },
            { icon: Calendar, title: "المناسبات", text: "أعراسنا، تجمعاتنا، وأخبار مجلس الذوادي على مدار العام.", to: "/events" },
          ].map((p) => (
            <Link
              key={p.title}
              to={p.to}
              className="group bg-background p-8 hover:bg-card transition-colors"
            >
              <p.icon className="h-7 w-7 text-accent" strokeWidth={1.4} />
              <h3 className="mt-6 font-display text-2xl text-foreground">{p.title}</h3>
              <p className="mt-3 text-sm text-muted-foreground leading-7">{p.text}</p>
              <span className="mt-6 inline-flex items-center gap-2 text-xs text-primary group-hover:gap-3 transition-all">
                <span>تصفّح</span>
                <ArrowLeft className="h-3.5 w-3.5" />
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* HERITAGE */}
      <section className="border-y border-border bg-card/40">
        <div className="mx-auto max-w-7xl px-6 py-24 grid gap-12 md:grid-cols-2 items-center">
          <div className="relative">
            <img
              src={heritageImage}
              alt="بيوت العائلة القديمة"
              width={1600}
              height={1067}
              loading="lazy"
              className="w-full aspect-[3/2] object-cover rounded-sm shadow-xl"
            />
            <div className="absolute -bottom-6 -left-6 hidden md:block w-40 aspect-[3/4] overflow-hidden rounded-sm border-4 border-background shadow-xl">
              <img src={palmImage} alt="نخلة" width={1200} height={1600} loading="lazy" className="w-full h-full object-cover" />
            </div>
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">من الذاكرة</p>
            <h2 className="mt-3 font-display text-4xl text-foreground">جذورٌ ضاربةٌ في الأرض</h2>
            <p className="mt-6 text-muted-foreground leading-9">
              نشأت عائلة الذوادي في كنف بيئةٍ خليجيةٍ أصيلة، تجمع بين كرم الصحراء
              وبركة البحر. ورّثنا الأجداد قيم النخوة والكرم، وحفظوا لنا الاسم نقيًّا،
              فاجتهد الأبناء في حفظ هذا الإرث ونقله إلى من بعدهم.
            </p>
            <p className="mt-4 text-muted-foreground leading-9">
              في هذه الصفحات، نُعيد سرد الحكاية: أسماءٌ، وجوهٌ، تواريخُ، ومجالسُ
              لا يجمعها إلا الدمُ والمحبة.
            </p>
            <Link to="/about" className="mt-8 inline-flex items-center gap-2 text-sm text-primary hover:gap-3 transition-all">
              <span>اقرأ تاريخ العائلة كاملًا</span>
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* INSTAGRAM CTA */}
      <section className="mx-auto max-w-5xl px-6 py-24 text-center">
        <p className="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">تابعنا</p>
        <h2 className="mt-3 font-display text-4xl text-foreground">مجلس الذوادي على إنستغرام</h2>
        <p className="mt-5 text-muted-foreground max-w-xl mx-auto leading-8">
          نشاركُ هناك آخر أخبار المجلس، صور التجمعات، ومناسبات العائلة الكريمة.
        </p>
        <a
          href="https://www.instagram.com/althawadi_majlis/?hl=ar"
          target="_blank"
          rel="noreferrer"
          className="mt-8 inline-flex items-center gap-3 rounded-sm border border-primary bg-background px-7 py-3 text-sm text-primary hover:bg-primary hover:text-primary-foreground transition-colors"
        >
          <span className="font-latin tracking-wider">@althawadi_majlis</span>
        </a>
      </section>
    </>
  );
}
