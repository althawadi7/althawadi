import { createFileRoute } from "@tanstack/react-router";
import { PageHero } from "@/components/PageHero";

export const Route = createFileRoute("/tree")({
  head: () => ({
    meta: [
      { title: "شجرة عائلة آل الذوادي" },
      { name: "description", content: "شجرة أنساب عائلة آل الذوادي من الجد المؤسس إلى الأحفاد." },
      { property: "og:title", content: "شجرة عائلة آل الذوادي" },
      { property: "og:url", content: "/tree" },
    ],
    links: [{ rel: "canonical", href: "/tree" }],
  }),
  component: TreePage,
});

type Node = { name: string; year?: string; children?: Node[] };

const tree: Node = {
  name: "الجدّ المؤسّس — الذوادي",
  year: "—",
  children: [
    {
      name: "الابن الأول",
      year: "—",
      children: [
        { name: "حفيد ١" },
        { name: "حفيد ٢" },
        { name: "حفيد ٣" },
      ],
    },
    {
      name: "الابن الثاني",
      year: "—",
      children: [
        { name: "حفيد ٤" },
        { name: "حفيد ٥" },
      ],
    },
    {
      name: "الابن الثالث",
      year: "—",
      children: [
        { name: "حفيد ٦" },
        { name: "حفيد ٧" },
        { name: "حفيد ٨" },
      ],
    },
  ],
};

function TreeNode({ node, root = false }: { node: Node; root?: boolean }) {
  return (
    <li className="relative flex flex-col items-center">
      <div
        className={`relative z-10 rounded-sm border px-5 py-3 text-center bg-background shadow-sm ${
          root ? "border-accent bg-accent/10" : "border-border"
        }`}
      >
        <div className="font-display text-base text-foreground whitespace-nowrap">{node.name}</div>
        {node.year && <div className="text-[10px] tracking-wider text-muted-foreground font-latin mt-0.5">{node.year}</div>}
      </div>

      {node.children && node.children.length > 0 && (
        <ul className="flex justify-center gap-6 pt-10 relative
          before:content-[''] before:absolute before:top-0 before:right-1/2 before:left-1/2 before:h-5 before:border-r before:border-border
          ">
          {node.children.map((c, i) => (
            <li
              key={i}
              className="relative pt-5
                before:content-[''] before:absolute before:top-0 before:right-1/2 before:left-1/2 before:h-5 before:border-r before:border-border
                after:content-[''] after:absolute after:top-0 after:h-px after:bg-border
                after:right-1/2 after:left-1/2
                first:after:right-1/2 first:after:left-0
                last:after:right-0 last:after:left-1/2
              "
            >
              <TreeNode node={c} />
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}

function TreePage() {
  return (
    <>
      <PageHero
        eyebrow="Family Tree — شجرة الأنساب"
        title="شجرةُ آل الذوادي"
        description="هذه شجرةٌ مبدئيّة قابلة للتحديث والتوسعة. ندعو جميع أبناء العائلة للمساهمة في إثرائها بالأسماء والتواريخ الموثّقة."
      />

      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="overflow-x-auto pb-6 -mx-6 px-6">
          <ul className="flex justify-center min-w-max">
            <TreeNode node={tree} root />
          </ul>
        </div>

        <p className="mt-12 text-center text-sm text-muted-foreground max-w-xl mx-auto leading-8">
          هل لديك معلومات تُكمل الشجرة؟ تواصل معنا لإضافة اسمك أو تصحيح ما يلزم،
          فهذه الذاكرة ملكٌ لنا جميعًا.
        </p>
      </section>
    </>
  );
}
