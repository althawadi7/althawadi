import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";

import appCss from "../styles.css?url";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";

function NotFoundComponent() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="max-w-md text-center">
        <h1 className="font-display text-7xl text-foreground">٤٠٤</h1>
        <p className="mt-4 text-muted-foreground">الصفحة المطلوبة غير موجودة.</p>
        <a href="/" className="mt-6 inline-block rounded-md bg-primary px-5 py-2 text-sm text-primary-foreground">العودة للرئيسية</a>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="max-w-md text-center">
        <h1 className="font-display text-2xl text-foreground">حدث خطأ غير متوقع</h1>
        <p className="mt-2 text-sm text-muted-foreground">يمكنك المحاولة مرة أخرى.</p>
        <button
          onClick={() => { router.invalidate(); reset(); }}
          className="mt-6 rounded-md bg-primary px-5 py-2 text-sm text-primary-foreground"
        >إعادة المحاولة</button>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "آل الذوادي — مجلس العائلة" },
      { name: "description", content: "الموقع الرسمي لعائلة آل الذوادي: تاريخنا، شجرة العائلة، الأجداد، الصور وأخبار المجلس." },
      { property: "og:title", content: "آل الذوادي — مجلس العائلة" },
      { property: "og:description", content: "تاريخ عائلة آل الذوادي، شجرة الأنساب، سير الأجداد ومعرض الصور." },
      { property: "og:type", content: "website" },
      { property: "og:site_name", content: "آل الذوادي" },
    ],
    links: [{ rel: "stylesheet", href: appCss }],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen flex flex-col">
        <SiteHeader />
        <main className="flex-1">
          <Outlet />
        </main>
        <SiteFooter />
      </div>
    </QueryClientProvider>
  );
}
