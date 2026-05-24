type Props = {
  eyebrow: string;
  title: string;
  description?: string;
};

export function PageHero({ eyebrow, title, description }: Props) {
  return (
    <section className="border-b border-border bg-card/40 paper-texture">
      <div className="mx-auto max-w-5xl px-6 py-20 text-center">
        <p className="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">{eyebrow}</p>
        <div className="ornament my-5 mx-auto w-40" />
        <h1 className="font-display text-4xl md:text-5xl text-foreground">{title}</h1>
        {description && (
          <p className="mt-6 max-w-2xl mx-auto text-muted-foreground leading-8">{description}</p>
        )}
      </div>
    </section>
  );
}
