import { Link } from "@tanstack/react-router";
import { useState } from "react";
import { Menu, X, Instagram } from "lucide-react";

const links = [
  { to: "/", label: "الرئيسية" },
  { to: "/about", label: "عن العائلة" },
  { to: "/tree", label: "شجرة العائلة" },
  { to: "/ancestors", label: "الأجداد" },
  { to: "/gallery", label: "الصور" },
  { to: "/news", label: "أخبار المجلس" },
  { to: "/events", label: "المناسبات" },
  { to: "/contact", label: "تواصل" },
] as const;

export function SiteHeader() {
  const [open, setOpen] = useState(false);
  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-3 group">
          <span className="grid h-10 w-10 place-items-center rounded-full border border-primary/40 font-display text-primary text-lg">ذ</span>
          <span className="leading-tight">
            <span className="block font-display text-lg text-foreground">آل الذوادي</span>
            <span className="block text-[11px] uppercase tracking-[0.25em] text-muted-foreground font-latin">AL Thawadi</span>
          </span>
        </Link>

        <nav className="hidden lg:flex items-center gap-7 text-sm">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className="text-foreground/70 hover:text-foreground transition-colors"
              activeProps={{ className: "text-accent font-semibold" }}
              activeOptions={{ exact: l.to === "/" }}
            >
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <a
            href="https://www.instagram.com/althawadi_majlis/?hl=ar"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-xs text-foreground/80 hover:bg-card transition-colors"
          >
            <Instagram className="h-3.5 w-3.5" />
            <span className="font-latin tracking-wide">@althawadi_majlis</span>
          </a>
          <button
            onClick={() => setOpen((v) => !v)}
            className="lg:hidden p-2 rounded-md hover:bg-card"
            aria-label="القائمة"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {open && (
        <div className="lg:hidden border-t border-border bg-background">
          <nav className="flex flex-col px-6 py-4 gap-3 text-sm">
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setOpen(false)}
                className="py-1 text-foreground/80"
                activeProps={{ className: "text-accent font-semibold" }}
                activeOptions={{ exact: l.to === "/" }}
              >
                {l.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
