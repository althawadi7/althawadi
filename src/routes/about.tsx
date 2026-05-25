import { createFileRoute } from "@tanstack/react-router";
import { PageHero } from "@/components/PageHero";
import palmImage from "@/assets/palm.jpg";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "عن عائلة الذوادي" },
      { name: "description", content: "تاريخ عائلة الذوادي، أصولها، قيمها، ومسيرتها عبر الأجيال." },
      { property: "og:title", content: "عن عائلة الذوادي" },
      { property: "og:description", content: "تاريخ ونشأة وقيم عائلة الذوادي." },
      { property: "og:url", content: "/about" },
    ],
    links: [{ rel: "canonical", href: "/about" }],
  }),
  component: AboutPage,
});

function AboutPage() {
  return (
    <>
      <PageHero
        eyebrow="About — عن العائلة"
        title="حكايةُ اسمٍ، ومسيرةُ أجيال"
        description="من جدٍّ مؤسّسٍ إلى أحفادٍ يحفظون الأمانة، تمتدّ عائلة الذوادي عبر الزمن بقيمٍ راسخة وأخلاقٍ موروثة."
      />

      <article className="mx-auto max-w-3xl px-6 py-20 prose-content">
        <div className="space-y-10 text-foreground/90 leading-9 text-lg">
          <section>
            <h2 className="font-display text-3xl text-foreground mb-4">الأصل والنشأة</h2>
            <p className="text-muted-foreground">
              تعود جذور عائلة الذوادي إلى أرضٍ خليجيةٍ عريقة، حيث استقرّ الجدّ الأكبر
              وأسّس بيتًا عُرف بالكرم والنخوة. ومنذ ذلك الحين، توارثت الأجيال هذا الاسم
              الكريم وحملته في كلّ مجلسٍ ومناسبة.
            </p>
          </section>

          <div className="my-12 -mx-6 md:mx-0">
            <img
              src={palmImage}
              alt="نخلة في الصحراء"
              width={1200}
              height={1600}
              loading="lazy"
              className="w-full aspect-[16/9] object-cover rounded-sm"
            />
          </div>

          <section>
            <h2 className="font-display text-3xl text-foreground mb-4">قيمنا</h2>
            <p className="text-muted-foreground">
              نحن في الذوادي نؤمن بأن العائلة هي السند الأول والأخير. نتمسّك بقيم
              صلة الرحم، وإكرام الضيف، ونصرة المظلوم، والحفاظ على الموروث الذي
              تركه لنا الآباء والأجداد.
            </p>
            <ul className="mt-6 grid gap-4 sm:grid-cols-2 not-prose">
              {[
                ["الكرم", "بابُ المجلس مفتوح، والمائدة عامرة."],
                ["النخوة", "الواحد منّا للجميع، والجميع للواحد."],
                ["العلم", "نشجّع أبناءنا على طلب المعرفة والتفوّق."],
                ["الذاكرة", "نحفظ سير من سبقونا ونوثّقها للأجيال."],
              ].map(([t, d]) => (
                <li key={t} className="border border-border rounded-sm p-5 bg-card/60">
                  <div className="font-display text-xl text-accent">{t}</div>
                  <p className="mt-1 text-sm text-muted-foreground leading-7">{d}</p>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h2 className="font-display text-3xl text-foreground mb-4">مجلس الذوادي اليوم</h2>
            <p className="text-muted-foreground">
              يضمّ مجلس الذوادي اليوم أبناءً وأحفادًا من مختلف الأجيال، يجتمعون
              في المناسبات السعيدة والحزينة، ويعملون يدًا واحدة على تعزيز روابط
              العائلة وتوثيق إرثها للأجيال القادمة.
            </p>
          </section>
        </div>
      </article>
    </>
  );
}
