#!/usr/bin/env python3
"""Shared site footer markup."""

BASE = "/althawadi"


def footer_nav_cols(base: str = BASE) -> str:
    return f"""        <div class="footer-nav-col">
          <h4 class="footer-nav-heading">الموقع</h4>
          <ul class="footer-nav-list">
            <li><a href="{base}/" data-home class="hover:text-accent">الرئيسية</a></li>
            <li><a href="{base}/about/" class="hover:text-accent">عن العائلة</a></li>
            <li><a href="{base}/contact/" class="hover:text-accent">تواصل</a></li>
          </ul>
        </div>
        <div class="footer-nav-col">
          <h4 class="footer-nav-heading">العائلة</h4>
          <ul class="footer-nav-list">
            <li><a href="{base}/tree/" class="hover:text-accent">شجرة العائلة</a></li>
            <li><a href="{base}/ancestors/" class="hover:text-accent">الأجداد</a></li>
          </ul>
        </div>
        <div class="footer-nav-col">
          <h4 class="footer-nav-heading">المحتوى</h4>
          <ul class="footer-nav-list">
            <li><a href="{base}/gallery/" class="hover:text-accent">الصور</a></li>
            <li><a href="{base}/news/" class="hover:text-accent">أخبار المجلس</a></li>
            <li><a href="{base}/references/" class="hover:text-accent">مراجع ومصادر</a></li>
          </ul>
        </div>"""


def footer_contact_col() -> str:
    return """        <div class="footer-contact-col">
          <h4 class="footer-nav-heading font-latin">تواصل</h4>
          <a href="https://www.instagram.com/althawadi_majlis/?hl=ar" target="_blank" rel="noreferrer" class="mt-4 inline-flex items-center gap-2 text-sm text-foreground/80 hover:text-accent">
            <svg class="icon h-4 w-4" viewBox="0 0 24 24" aria-hidden="true"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>
            <span class="font-latin">@althawadi_majlis</span>
          </a>
          <p class="mt-4 text-sm text-muted-foreground leading-7">للتواصل والمساهمة بالمعلومات والصور: <a href="/althawadi/contact/" class="text-accent hover:underline">صفحة التواصل</a></p>
        </div>"""
