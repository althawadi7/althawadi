import { Link } from "@tanstack/react-router";
import { Instagram } from "lucide-react";

export function SiteFooter() {
  return (
    <footer className="mt-24 border-t border-border bg-card/40">
      <div className="mx-auto max-w-7xl px-6 py-14 grid gap-10 md:grid-cols-3">
        <div>
          <div className="font-display text-2xl text-foreground">آل الذوادي</div>
          <p className="mt-3 text-sm text-muted-foreground leading-7 max-w-sm">
            بيت من الذكريات، وصفحة من التاريخ. نوثّق هنا نسب عائلتنا، وسير أجدادنا،
            وصورًا تحكي مسيرتنا جيلًا بعد جيل.
          </p>
        </div>

        <div>
          <h4 className="text-xs uppercase tracking-[0.3em] text-muted-foreground font-latin">روابط</h4>
          <ul className="mt-4 space-y-2 text-sm">
            <li><Link to="/about" className="hover:text-accent">عن العائلة</Link></li>
            <li><Link to="/tree" className="hover:text-accent">شجرة العائلة</Link></li>
            <li><Link to="/ancestors" className="hover:text-accent">الأجداد</Link></li>
            <li><Link to="/gallery" className="hover:text-accent">الصور</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-xs uppercase tracking-[0.3em] text-muted-foreground font-latin">تواصل</h4>
          <a
            href="https://www.instagram.com/althawadi_majlis/?hl=ar"
            target="_blank"
            rel="noreferrer"
            className="mt-4 inline-flex items-center gap-2 text-sm text-foreground/80 hover:text-accent"
          >
            <Instagram className="h-4 w-4" />
            <span className="font-latin">@althawadi_majlis</span>
          </a>
          <p className="mt-4 text-sm text-muted-foreground">
            للتواصل والمساهمة بالمعلومات والصور:
            <Link to="/contact" className="text-accent hover:underline mr-1">صفحة التواصل</Link>
          </p>
        </div>
      </div>
      <div className="border-t border-border/60">
        <div className="mx-auto max-w-7xl px-6 py-5 text-xs text-muted-foreground flex flex-wrap justify-between gap-3">
          <span>© {new Date().getFullYear()} مجلس آل الذوادي — جميع الحقوق محفوظة</span>
          <span className="font-latin tracking-[0.2em] uppercase">AL Thawadi Family</span>
        </div>
      </div>
    </footer>
  );
}
