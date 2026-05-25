import { createFileRoute } from "@tanstack/react-router";
import { PageHero } from "@/components/PageHero";
import heroImage from "@/assets/hero-majlis.jpg";
import heritageImage from "@/assets/heritage.jpg";
import palmImage from "@/assets/palm.jpg";

export const Route = createFileRoute("/gallery")({
  head: () => ({
    meta: [
      { title: "معرض صور عائلة الذوادي" },
      { name: "description", content: "صور أرشيفية وعائلية تختزن لحظات من تاريخ عائلة الذوادي." },
      { property: "og:title", content: "معرض صور الذوادي" },
      { property: "og:url", content: "/gallery" },
    ],
    links: [{ rel: "canonical", href: "/gallery" }],
  }),
  component: GalleryPage,
});

const photos = [
  { src: heroImage, title: "مجلس العائلة", caption: "صورةٌ من المجلس في زمنٍ مضى." },
  { src: heritageImage, title: "البيوت القديمة", caption: "حيث نشأ الجدّ وكبر الأبناء." },
  { src: palmImage, title: "نخلةُ الدار", caption: "ظلٌّ امتدّ على أجيال." },
  { src: heroImage, title: "ضيافة المجلس", caption: "كرمُ الذوادي معروف." },
  { src: heritageImage, title: "أحياء الذاكرة", caption: "أزقّةٌ تذكرنا بالأمس." },
  { src: palmImage, title: "تحت ظلال النخيل", caption: "هنا اجتمع الأهل." },
];

function GalleryPage() {
  return (
    <>
      <PageHero
        eyebrow="Gallery — معرض الصور"
        title="ذاكرةٌ في صور"
        description="كلّ صورةٍ حكاية. هذه مجموعة مبدئيّة من صور العائلة، وندعو الجميع لإثرائها بصورهم الأرشيفية."
      />

      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="columns-1 sm:columns-2 lg:columns-3 gap-6 [column-fill:_balance]">
          {photos.map((p, i) => (
            <figure
              key={i}
              className="mb-6 break-inside-avoid group overflow-hidden rounded-sm border border-border bg-card"
            >
              <div className="overflow-hidden">
                <img
                  src={p.src}
                  alt={p.title}
                  loading="lazy"
                  className="w-full h-auto object-cover group-hover:scale-[1.03] transition-transform duration-700"
                />
              </div>
              <figcaption className="p-4 border-t border-border">
                <div className="font-display text-lg text-foreground">{p.title}</div>
                <p className="text-xs text-muted-foreground mt-1">{p.caption}</p>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>
    </>
  );
}
