import os
import json
import re
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "portfolio_data.json"
INDEX_FILE = "index.html"
PROJECTS_DIR = "projects"

DEFAULT_DATA = [
    {
        "id": "falfol-identity",
        "title": "فلفول الشام — هوية بصرية",
        "subtitle": "تصميم الهوية البصرية المتكاملة، الشعار، ودليل الاستخدام",
        "category": ["identity"],
        "type": "visual_identity",
        "thumbnail": "https://res.cloudinary.com/di8ioqtv/image/upload/f_auto/q_auto/v1792356043/falfol-cover.png",
        "lightbox_media_type": "image",
        "lightbox_media_url": "",
        "pdf_url": "",
        "client": "فلفول الشام",
        "role": "Brand Identity & Art Direction",
        "disciplines": "Visual Identity, Typography, Packaging",
        "year": "2026",
        "overview": "بناء هوية بصرية متكاملة وشاملة تعكس أصالة المأكولات الشامية بطابع عصري جذاب، تشمل بناء الشعار، فلسفة الألوان، تطبيقات المطبوعات والتغليف، ودليل الهوية الكامل.",
        "deliverables": [
            "Primary & Secondary Logo Marks",
            "Color Palette & Font Pairing",
            "Packaging & Uniform Design",
            "Brand Guidelines Manual (PDF)"
        ],
        "gallery_images": [
            "https://res.cloudinary.com/di8ioqtv/image/upload/f_auto/q_auto/v1792356043/falfol-cover.png"
        ],
        "video_embed_url": ""
    }
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    if isinstance(item.get("category"), str):
                        item["category"] = [item["category"]]
                return data
        except Exception:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def format_video_embed(url, autoplay=False):
    url = url.strip()
    if not url:
        return ""

    if "<iframe" in url and 'src="' in url:
        url = url.split('src="')[1].split('"')[0]

    ap_param = "autoplay=1&mute=1" if autoplay else "autoplay=0"

    if "youtube.com/watch" in url and "v=" in url:
        video_id = url.split("v=")[1].split("&")[0].split("?")[0]
        return f"https://www.youtube-nocookie.com/embed/{video_id}?{ap_param}&rel=0"

    if "youtube.com/embed/" in url:
        video_id = url.split("youtube.com/embed/")[1].split("?")[0].split("&")[0]
        return f"https://www.youtube-nocookie.com/embed/{video_id}?{ap_param}&rel=0"

    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
        return f"https://www.youtube-nocookie.com/embed/{video_id}?{ap_param}&rel=0"

    if "youtube.com/shorts/" in url:
        video_id = url.split("youtube.com/shorts/")[1].split("?")[0].split("&")[0]
        return f"https://www.youtube-nocookie.com/embed/{video_id}?{ap_param}&rel=0"

    if "vimeo.com/" in url and "player.vimeo.com" not in url:
        parts = url.replace("https://vimeo.com/", "").replace("http://vimeo.com/", "").split("?")[0].split("/")
        video_id = parts[0]
        hash_param = f"?h={parts[1]}" if len(parts) > 1 else "?"
        vimeo_ap = "&autoplay=1" if autoplay else ""
        return f"https://player.vimeo.com/video/{video_id}{hash_param}{vimeo_ap}"

    return url

def format_pdf_embed(url):
    """Converts Drive and cloud PDF links into embed-ready iframe sources."""
    url = url.strip()
    if not url:
        return ""
    if "drive.google.com" in url:
        if "/view" in url:
            return url.replace("/view", "/preview")
        elif "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
            return f"https://drive.google.com/file/d/{file_id}/preview"
    return url

def generate_card_html(project):
    p_type = project.get("type", "lightbox")
    cats = project.get("category", ["identity"])
    if isinstance(cats, str):
        cats = [cats]
    category_attr = " ".join(cats)

    title = project.get("title", "")
    subtitle = project.get("subtitle", "")
    thumb = project.get("thumbnail", "")
    p_id = project.get("id", "")

    cat_labels = {
        "identity": "Visual Identity",
        "social": "Social Media",
        "motion": "Motion Graphics",
        "photo": "Photography",
        "prints": "Prints & Packaging",
        "montage": "Montage & Reels"
    }

    if p_type == "visual_identity":
        badge = "Visual Identity"
    elif p_type == "case_study":
        badge = "Case Study"
    else:
        badge = cat_labels.get(cats[0], "Design") if cats else "Design"

    if not thumb or "vimeo.com" in thumb or "youtube.com" in thumb or "youtu.be" in thumb:
        thumb = "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80"

    # Both case studies and visual identity modes render as rich project pages
    if p_type in ["case_study", "visual_identity"]:
        return f"""          <!-- Project Card: {title} -->
          <a href="projects/{p_id}.html" class="project-card glow-hover block rounded-3xl bg-brand-card overflow-hidden border border-white/10 group cursor-pointer" data-category="{category_attr}" data-project-type="{p_type}" data-cursor="hover">
            <div class="relative aspect-square overflow-hidden bg-zinc-900">
              <img src="{thumb}" alt="{title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
              <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-80 group-hover:opacity-95 transition-opacity"></div>
              <div class="absolute top-4 inset-x-4 flex items-center justify-between">
                <span class="px-3 py-1 rounded-lg bg-black/60 backdrop-blur-md text-[11px] font-bold text-brand-yellow uppercase tracking-wider">{badge}</span>
                <div class="w-8 h-8 rounded-full bg-black/60 backdrop-blur-md text-white group-hover:bg-brand-yellow group-hover:text-black flex items-center justify-center transition-all duration-300">
                  <i data-lucide="arrow-up-right" class="w-4 h-4"></i>
                </div>
              </div>
              <div class="absolute bottom-4 inset-x-4">
                <h3 class="text-lg font-bold text-white group-hover:text-brand-yellow transition-colors">{title}</h3>
                <p class="text-xs text-gray-300 mt-1 line-clamp-1">{subtitle}</p>
              </div>
            </div>
          </a>\n"""
    else:
        media_type = project.get("lightbox_media_type", "image")
        raw_media_url = project.get("lightbox_media_url", "")
        if not raw_media_url:
            raw_media_url = thumb

        is_vertical = any(k in raw_media_url.lower() for k in ["/shorts/", "#vertical", "#short", "#reel", "tiktok.com", "instagram.com/reel"])
        orientation = "vertical" if is_vertical else "landscape"

        play_btn = ""
        if media_type == "video":
            clean_url = re.sub(r'#(vertical|short|reel|portrait)\b', '', raw_media_url, flags=re.IGNORECASE).strip()
            media_url = format_video_embed(clean_url, autoplay=True)
            play_btn = """              <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-14 h-14 rounded-full bg-brand-yellow/90 text-black flex items-center justify-center group-hover:scale-110 shadow-lg shadow-brand-yellow/30 transition-transform">
                  <i data-lucide="play" class="w-6 h-6 fill-current"></i>
                </div>
              </div>\n"""
        else:
            media_url = raw_media_url

        return f"""          <!-- Project Card: {title} -->
          <div class="project-card glow-hover rounded-3xl bg-brand-card overflow-hidden border border-white/10 group cursor-pointer" data-category="{category_attr}" data-project-type="lightbox" data-media-type="{media_type}" data-orientation="{orientation}" data-media-url="{media_url}" data-title="{title}" data-desc="{subtitle}" data-cursor="hover">
            <div class="relative aspect-square overflow-hidden bg-zinc-900">
              <img src="{thumb}" alt="{title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
              <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-80 group-hover:opacity-95 transition-opacity"></div>
{play_btn}              <div class="absolute top-4 left-4">
                <span class="px-3 py-1 rounded-lg bg-black/60 backdrop-blur-md text-[11px] font-bold text-brand-yellow uppercase tracking-wider">{badge}</span>
              </div>
              <div class="absolute bottom-4 inset-x-4">
                <h3 class="text-lg font-bold text-white group-hover:text-brand-yellow transition-colors">{title}</h3>
                <p class="text-xs text-gray-300 mt-1 line-clamp-1">{subtitle}</p>
              </div>
            </div>
          </div>\n"""

def generate_visual_identity_page(project):
    """Generates a specialized showcase page tailored for Visual Identity, Brand Books, and Guidelines."""
    title = project.get("title", "")
    client = project.get("client", "Client Name")
    role = project.get("role", "Brand Identity & Art Direction")
    disciplines = project.get("disciplines", "Visual Identity, Typography, Packaging")
    year = project.get("year", "2026")
    overview = project.get("overview", "")
    deliverables = project.get("deliverables", [])
    gallery = project.get("gallery_images", [])
    pdf_url = project.get("pdf_url", "").strip()

    deliv_items = "".join([f'<li class="flex items-center gap-2"><i data-lucide="check" class="w-3.5 h-3.5 text-brand-yellow"></i> {d}</li>\n' for d in deliverables])

    # PDF Action Buttons in Header
    pdf_header_cta = ""
    pdf_embed_section = ""
    if pdf_url:
        embed_src = format_pdf_embed(pdf_url)
        pdf_header_cta = f"""
        <div class="flex flex-wrap items-center gap-3 mt-6">
          <a href="#brandManual" class="px-6 py-3 rounded-xl bg-brand-yellow text-black font-bold text-xs hover:bg-yellow-400 transition-all flex items-center gap-2 shadow-lg shadow-brand-yellow/20">
            <i data-lucide="book-open" class="w-4 h-4"></i>
            <span>تصفح دليل الهوية الرقمي (PDF)</span>
          </a>
          <a href="{pdf_url}" target="_blank" download class="px-5 py-3 rounded-xl bg-brand-card hover:bg-white/10 text-white font-semibold text-xs border border-white/10 transition-all flex items-center gap-2">
            <i data-lucide="download" class="w-4 h-4 text-brand-yellow"></i>
            <span>تحميل الدليل المباشر</span>
          </a>
        </div>"""

        pdf_embed_section = f"""
    <!-- Interactive Brand Guidelines PDF Viewer -->
    <section id="brandManual" class="space-y-4 pt-8">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-3xl bg-brand-surface border border-white/10">
        <div>
          <h3 class="text-lg font-bold text-brand-yellow flex items-center gap-2">
            <i data-lucide="book-open" class="w-5 h-5 text-brand-yellow"></i>
            <span>دليل واستخدامات الهوية البصرية (Brand Guidelines)</span>
          </h3>
          <p class="text-xs text-gray-400 mt-1">تصفح الدليل الكامل للهوية بجميع صفحاته ومعاييره، أو قم بتحميله كملف مرجعي.</p>
        </div>
        <div class="flex items-center gap-3 shrink-0">
          <a href="{pdf_url}" target="_blank" download class="px-5 py-2.5 rounded-xl bg-brand-yellow text-black text-xs font-bold hover:bg-yellow-400 transition-all flex items-center gap-2">
            <i data-lucide="download" class="w-4 h-4"></i>
            <span>تحميل PDF</span>
          </a>
          <a href="{pdf_url}" target="_blank" class="px-4 py-2.5 rounded-xl bg-brand-card hover:bg-white/10 text-white text-xs font-semibold border border-white/10 transition-all flex items-center gap-2">
            <i data-lucide="external-link" class="w-4 h-4"></i>
            <span>فتح في نافذة كاملة</span>
          </a>
        </div>
      </div>
      <div class="w-full h-[75vh] sm:h-[88vh] rounded-3xl overflow-hidden border border-white/10 bg-zinc-950 shadow-2xl">
        <iframe src="{embed_src}" class="w-full h-full" frameborder="0" allowfullscreen></iframe>
      </div>
    </section>"""

    # High-impact presentation boards stack
    gallery_html = ""
    if gallery:
        board_items = ""
        for idx, img in enumerate(gallery):
            img_url = img.strip()
            if not img_url:
                continue
            board_items += f"""
        <div class="case-study-thumb group relative rounded-3xl overflow-hidden border border-white/10 bg-brand-surface cursor-pointer shadow-xl hover:border-brand-yellow/30 transition-all" data-full-src="{img_url}">
          <img src="{img_url}" alt="Brand Presentation Board {idx + 1}" class="w-full h-auto object-cover group-hover:scale-[1.02] transition-transform duration-500" loading="lazy" />
          <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <div class="w-12 h-12 rounded-full bg-brand-yellow text-black flex items-center justify-center shadow-lg transform translate-y-2 group-hover:translate-y-0 transition-all">
              <i data-lucide="maximize-2" class="w-5 h-5"></i>
            </div>
          </div>
        </div>\n"""

        gallery_html = f"""
    <!-- Visual Identity Presentation Boards (Full Detail) -->
    <section class="space-y-6 pt-4">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest">لوحات العرض وتطبيقات الهوية (اضغط للتكبير)</h3>
        <span class="text-xs text-brand-yellow font-mono">{len(gallery)} لوحات</span>
      </div>
      <div class="space-y-8">
        {board_items}
      </div>
    </section>"""

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl" class="scroll-smooth">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <title>{title} | DAOUD DESIGN</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{ brand: {{ yellow: '#F59E0B', dark: '#0B0B0E', surface: '#141418', card: '#1B1B22' }} }},
          fontFamily: {{ sans: ['Cairo', 'Plus Jakarta Sans', 'sans-serif'] }}
        }}
      }}
    }};
  </script>
</head>
<body class="bg-brand-dark text-gray-200 antialiased font-sans selection:bg-brand-yellow selection:text-black">
  <nav class="fixed top-6 inset-x-0 z-50 max-w-5xl mx-auto px-6">
    <div class="h-14 px-6 rounded-2xl bg-brand-surface/85 backdrop-blur-md border border-white/10 flex items-center justify-between shadow-2xl">
      <a href="../index.html#portfolio" class="flex items-center gap-2 text-xs sm:text-sm font-bold text-gray-300 hover:text-brand-yellow transition-colors group">
        <i data-lucide="arrow-right" class="w-4 h-4 group-hover:-translate-x-1 transition-transform rtl:rotate-0 ltr:rotate-180"></i>
        <span>العودة لمعرض الأعمال</span>
      </a>
      <span class="text-xs font-mono text-brand-yellow font-bold uppercase">{year}</span>
    </div>
  </nav>

  <header class="pt-32 pb-14 max-w-5xl mx-auto px-6">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-brand-yellow/10 border border-brand-yellow/30 text-brand-yellow text-xs font-bold uppercase tracking-wider mb-4">
      <i data-lucide="palette" class="w-3.5 h-3.5"></i>
      <span>هوية بصرية متكاملة (Visual Identity)</span>
    </div>
    <h1 class="text-3xl sm:text-5xl font-black text-white leading-tight">{title}</h1>
    {pdf_header_cta}

    <div class="grid grid-cols-2 sm:grid-cols-4 gap-6 mt-12 py-8 border-y border-white/10 text-sm">
      <div>
        <span class="block text-xs font-medium text-gray-500 uppercase">العميل</span>
        <span class="font-bold text-white mt-1 block">{client}</span>
      </div>
      <div>
        <span class="block text-xs font-medium text-gray-500 uppercase">المسؤولية</span>
        <span class="font-bold text-white mt-1 block">{role}</span>
      </div>
      <div>
        <span class="block text-xs font-medium text-gray-500 uppercase">المخرجات</span>
        <span class="font-bold text-white mt-1 block">{disciplines}</span>
      </div>
      <div>
        <span class="block text-xs font-medium text-gray-500 uppercase">السنة</span>
        <span class="font-bold text-white mt-1 block">{year}</span>
      </div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-6 pb-24 space-y-16">
    <section class="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
      <div class="md:col-span-2">
        <h2 class="text-xl font-bold text-brand-yellow mb-3">نظرة عامة على المشروع</h2>
        <p class="text-gray-300 leading-relaxed text-sm sm:text-base font-light">{overview}</p>
      </div>
      <div class="p-6 rounded-2xl bg-brand-card/70 border border-white/5 space-y-3">
        <h3 class="text-xs font-bold text-brand-yellow uppercase tracking-wider">مكونات الهوية المنفذة</h3>
        <ul class="text-xs text-gray-300 space-y-2">
          {deliv_items}
        </ul>
      </div>
    </section>

    {pdf_embed_section}
    {gallery_html}

    <footer class="pt-16 border-t border-white/10 flex justify-between items-center">
      <a href="../index.html#portfolio" class="px-6 py-3 rounded-xl bg-brand-card hover:bg-brand-surface border border-white/10 text-xs font-bold text-white transition-all flex items-center gap-2">
        <i data-lucide="grid" class="w-4 h-4 text-brand-yellow"></i>
        <span>عرض كافة المشاريع</span>
      </a>
    </footer>
  </main>

  <div id="imageLightbox" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 bg-black/95 backdrop-blur-xl opacity-0 pointer-events-none transition-all duration-300">
    <button id="closeLightbox" class="absolute top-6 right-6 z-20 w-11 h-11 rounded-full bg-white/10 hover:bg-brand-yellow text-white hover:text-black flex items-center justify-center transition-colors">
      <i data-lucide="x" class="w-6 h-6"></i>
    </button>
    <div class="relative max-w-5xl max-h-[90vh] flex items-center justify-center">
      <img id="lightboxTarget" src="" alt="Enlarged preview" class="max-w-full max-h-[85vh] object-contain rounded-2xl shadow-2xl border border-white/10" />
    </div>
  </div>

  <script>
    lucide.createIcons();
    const lightbox = document.getElementById('imageLightbox');
    const lightboxImg = document.getElementById('lightboxTarget');
    const closeBtn = document.getElementById('closeLightbox');

    document.querySelectorAll('.case-study-thumb').forEach(thumb => {{
      thumb.addEventListener('click', () => {{
        lightboxImg.src = thumb.dataset.fullSrc;
        lightbox.classList.remove('opacity-0', 'pointer-events-none');
        document.body.style.overflow = 'hidden';
      }});
    }});

    function hideLightbox() {{
      lightbox.classList.add('opacity-0', 'pointer-events-none');
      document.body.style.overflow = '';
      setTimeout(() => {{ lightboxImg.src = ''; }}, 200);
    }}

    closeBtn.addEventListener('click', hideLightbox);
    lightbox.addEventListener('click', (e) => {{ if (e.target === lightbox) hideLightbox(); }});
    window.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') hideLightbox(); }});
  </script>
</body>
</html>"""

def generate_case_study_page(project):
    title = project.get("title", "")
    client = project.get("client", "Client Name")
    role = project.get("role", "Art Direction & Visuals")
    disciplines = project.get("disciplines", "Design, Motion, Video")
    year = project.get("year", "2026")
    overview = project.get("overview", "")
    deliverables = project.get("deliverables", [])
    gallery = project.get("gallery_images", [])
    raw_video_input = project.get("video_embed_url", "")

    deliv_items = "".join([f'<li class="flex items-center gap-2"><i data-lucide="check" class="w-3.5 h-3.5 text-brand-yellow"></i> {d}</li>\n' for d in deliverables])

    gallery_html = ""
    if gallery:
        gallery_items = ""
        for idx, img in enumerate(gallery):
            img_url = img.strip()
            if not img_url:
                continue
            gallery_items += f"""
          <div class="case-study-thumb group relative rounded-2xl overflow-hidden border border-white/10 bg-brand-surface cursor-pointer aspect-square" data-full-src="{img_url}">
            <img src="{img_url}" alt="Asset {idx + 1}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
            <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <div class="w-10 h-10 rounded-full bg-brand-yellow text-black flex items-center justify-center shadow-lg transform translate-y-2 group-hover:translate-y-0 transition-all duration-300">
                <i data-lucide="maximize-2" class="w-5 h-5"></i>
              </div>
            </div>
          </div>\n"""

        gallery_html = f"""
    <section class="space-y-4 pt-4">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest">معرض محتويات الحملة (اضغط للتكبير)</h3>
        <span class="text-xs text-brand-yellow font-mono">{len(gallery)} تصاميم</span>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {gallery_items}
      </div>
    </section>"""

    video_html = ""
    if raw_video_input:
        wide_videos = []
        short_videos = []

        for line in raw_video_input.splitlines():
            line = line.strip().rstrip(',')
            if not line:
                continue

            is_vertical = any(k in line.lower() for k in ["/shorts/", "#vertical", "#short", "#reel", "tiktok.com", "instagram.com/reel"])
            clean_line = re.sub(r'#(vertical|short|reel|portrait)\b', '', line, flags=re.IGNORECASE).strip()
            embed_url = format_video_embed(clean_line, autoplay=False)

            if embed_url:
                if is_vertical:
                    short_videos.append(embed_url)
                else:
                    wide_videos.append(embed_url)

        total_videos = len(wide_videos) + len(short_videos)

        if total_videos > 0:
            video_sections = []

            if wide_videos:
                if len(wide_videos) == 1:
                    wide_markup = f"""
        <div class="aspect-video w-full rounded-3xl overflow-hidden border border-white/10 bg-black shadow-2xl hover:border-brand-yellow/40 transition-all">
          <iframe src="{wide_videos[0]}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen class="w-full h-full"></iframe>
        </div>"""
                else:
                    cards = "".join([f"""
        <div class="aspect-video w-full rounded-2xl overflow-hidden border border-white/10 bg-black shadow-2xl hover:border-brand-yellow/40 transition-all">
          <iframe src="{u}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen class="w-full h-full"></iframe>
        </div>\n""" for u in wide_videos])
                    wide_markup = f"""
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {cards}
        </div>"""

                subheading = '<h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">فيديوهات الإنتاج والمونتاج (16:9)</h4>' if short_videos else ''
                video_sections.append(f"""
        <div>
          {subheading}
          {wide_markup}
        </div>""")

            if short_videos:
                cards = "".join([f"""
        <div class="aspect-[9/16] w-full rounded-3xl overflow-hidden border border-white/10 bg-black shadow-2xl hover:border-brand-yellow/40 transition-all">
          <iframe src="{u}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen class="w-full h-full"></iframe>
        </div>\n""" for u in short_videos])
                short_markup = f"""
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {cards}
        </div>"""

                subheading = '<h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">فيديوهات ريلز وشورتس (9:16 Shorts)</h4>' if wide_videos else ''
                video_sections.append(f"""
        <div class="pt-4">
          {subheading}
          {short_markup}
        </div>""")

            combined_layout = "\n".join(video_sections)
            video_html = f"""
    <section class="space-y-6 pt-8">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-bold text-brand-yellow">الموشن جرافيك والمونتاج</h3>
        <span class="text-xs text-brand-yellow font-mono">{total_videos} فيديوهات</span>
      </div>
      {combined_layout}
    </section>"""

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl" class="scroll-smooth">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <title>{title} | DAOUD DESIGN</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{ brand: {{ yellow: '#F59E0B', dark: '#0B0B0E', surface: '#141418', card: '#1B1B22' }} }},
          fontFamily: {{ sans: ['Cairo', 'Plus Jakarta Sans', 'sans-serif'] }}
        }}
      }}
    }};
  </script>
</head>
<body class="bg-brand-dark text-gray-200 antialiased font-sans selection:bg-brand-yellow selection:text-black">
  <nav class="fixed top-6 inset-x-0 z-50 max-w-5xl mx-auto px-6">
    <div class="h-14 px-6 rounded-2xl bg-brand-surface/85 backdrop-blur-md border border-white/10 flex items-center justify-between shadow-2xl">
      <a href="../index.html#portfolio" class="flex items-center gap-2 text-xs sm:text-sm font-bold text-gray-300 hover:text-brand-yellow transition-colors group">
        <i data-lucide="arrow-right" class="w-4 h-4 group-hover:-translate-x-1 transition-transform rtl:rotate-0 ltr:rotate-180"></i>
        <span>العودة لمعرض الأعمال</span>
      </a>
      <span class="text-xs font-mono text-brand-yellow font-bold uppercase">{year}</span>
    </div>
  </nav>

  <header class="pt-32 pb-14 max-w-5xl mx-auto px-6">
    <h1 class="text-3xl sm:text-5xl font-black text-white mt-4 leading-tight">{title}</h1>
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-6 mt-12 py-8 border-y border-white/10 text-sm">
      <div>
        <span class="block text-xs font-medium text-gray-500 uppercase">العميل</span>
        <span class="font-bold text-white mt-1 block">{client}</span>
      </div>
      <div>
        <span class="block text-xs font-medium text-gray-500 uppercase">المسؤولية</span>
        <span class="font-bold text-white mt-1 block">{role}</span>
      </div>
      <div>
        <span class="block text-xs font-medium text-gray-500 uppercase">التخصصات</span>
        <span class="font-bold text-white mt-1 block">{disciplines}</span>
      </div>
      <div>
        <span class="block text-xs font-medium text-gray-500 uppercase">السنة</span>
        <span class="font-bold text-white mt-1 block">{year}</span>
      </div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-6 pb-24 space-y-16">
    <section class="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
      <div class="md:col-span-2">
        <h2 class="text-xl font-bold text-brand-yellow mb-3">نظرة عامة على المشروع</h2>
        <p class="text-gray-300 leading-relaxed text-sm sm:text-base font-light">{overview}</p>
      </div>
      <div class="p-6 rounded-2xl bg-brand-card/70 border border-white/5 space-y-3">
        <h3 class="text-xs font-bold text-brand-yellow uppercase tracking-wider">المخرجات المنفذة</h3>
        <ul class="text-xs text-gray-300 space-y-2">
          {deliv_items}
        </ul>
      </div>
    </section>

    {gallery_html}
    {video_html}

    <footer class="pt-16 border-t border-white/10 flex justify-between items-center">
      <a href="../index.html#portfolio" class="px-6 py-3 rounded-xl bg-brand-card hover:bg-brand-surface border border-white/10 text-xs font-bold text-white transition-all flex items-center gap-2">
        <i data-lucide="grid" class="w-4 h-4 text-brand-yellow"></i>
        <span>عرض كافة المشاريع</span>
      </a>
    </footer>
  </main>

  <div id="imageLightbox" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 bg-black/95 backdrop-blur-xl opacity-0 pointer-events-none transition-all duration-300">
    <button id="closeLightbox" class="absolute top-6 right-6 z-20 w-11 h-11 rounded-full bg-white/10 hover:bg-brand-yellow text-white hover:text-black flex items-center justify-center transition-colors">
      <i data-lucide="x" class="w-6 h-6"></i>
    </button>
    <div class="relative max-w-5xl max-h-[90vh] flex items-center justify-center">
      <img id="lightboxTarget" src="" alt="Enlarged preview" class="max-w-full max-h-[85vh] object-contain rounded-2xl shadow-2xl border border-white/10" />
    </div>
  </div>

  <script>
    lucide.createIcons();
    const lightbox = document.getElementById('imageLightbox');
    const lightboxImg = document.getElementById('lightboxTarget');
    const closeBtn = document.getElementById('closeLightbox');

    document.querySelectorAll('.case-study-thumb').forEach(thumb => {{
      thumb.addEventListener('click', () => {{
        lightboxImg.src = thumb.dataset.fullSrc;
        lightbox.classList.remove('opacity-0', 'pointer-events-none');
        document.body.style.overflow = 'hidden';
      }});
    }});

    function hideLightbox() {{
      lightbox.classList.add('opacity-0', 'pointer-events-none');
      document.body.style.overflow = '';
      setTimeout(() => {{ lightboxImg.src = ''; }}, 200);
    }}

    closeBtn.addEventListener('click', hideLightbox);
    lightbox.addEventListener('click', (e) => {{ if (e.target === lightbox) hideLightbox(); }});
    window.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') hideLightbox(); }});
  </script>
</body>
</html>"""

def build_website():
    data = load_data()
    os.makedirs(PROJECTS_DIR, exist_ok=True)

    for item in data:
        p_type = item.get("type")
        p_id = item.get("id")
        if p_type == "case_study":
            file_path = os.path.join(PROJECTS_DIR, f"{p_id}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(generate_case_study_page(item))
        elif p_type == "visual_identity":
            file_path = os.path.join(PROJECTS_DIR, f"{p_id}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(generate_visual_identity_page(item))

    if not os.path.exists(INDEX_FILE):
        messagebox.showerror("Error", f"Could not find {INDEX_FILE} in current directory.")
        return False

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    start_tag = "<!-- PROJECTS_START -->"
    end_tag = "<!-- PROJECTS_END -->"

    if start_tag not in content or end_tag not in content:
        messagebox.showerror(
            "Markers Missing",
            f"Please insert {start_tag} and {end_tag} inside your #portfolioGrid in {INDEX_FILE}."
        )
        return False

    cards_markup = "\n" + "".join([generate_card_html(item) for item in data]) + "          "
    before = content.split(start_tag)[0] + start_tag
    after = end_tag + content.split(end_tag)[1]
    new_content = before + cards_markup + after

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True

server_started = False
def start_local_server_and_open():
    global server_started
    port = 8000

    def run_server():
        server_address = ('', port)
        httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
        httpd.serve_forever()

    if not server_started:
        threading.Thread(target=run_server, daemon=True).start()
        server_started = True

    webbrowser.open(f"http://localhost:{port}/index.html")

class PortfolioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daoud Design - Portfolio Project Manager")
        self.root.geometry("960x650")
        self.root.minsize(820, 520)
        self.root.configure(bg="#0B0B0E")

        self.projects = load_data()
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        header = tk.Frame(self.root, bg="#141418", height=60)
        header.pack(fill="x", side="top")

        lbl_title = tk.Label(header, text="DAOUD DESIGN — Portfolio Manager", font=("Arial", 14, "bold"), fg="#F59E0B", bg="#141418")
        lbl_title.pack(side="left", padx=20, pady=15)

        btn_preview = tk.Button(header, text="🌐 Preview Website", font=("Arial", 10, "bold"), bg="#3B82F6", fg="#FFFFFF", padx=12, pady=6, bd=0, cursor="hand2", command=start_local_server_and_open)
        btn_preview.pack(side="right", padx=(5, 20))

        btn_build = tk.Button(header, text="⚡ Build & Update Website", font=("Arial", 10, "bold"), bg="#F59E0B", fg="#000000", padx=15, pady=6, bd=0, cursor="hand2", command=self.on_build)
        btn_build.pack(side="right", padx=5)

        body = tk.Frame(self.root, bg="#0B0B0E")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        left_frame = tk.Frame(body, bg="#141418", bd=1, relief="solid")
        left_frame.pack(side="left", fill="both", expand=True)

        lbl_list = tk.Label(left_frame, text="Active Portfolio Projects", font=("Arial", 11, "bold"), fg="#FFFFFF", bg="#141418")
        lbl_list.pack(anchor="w", padx=15, pady=10)

        self.tree = ttk.Treeview(left_frame, columns=("title", "category", "type"), show="headings", height=15)
        self.tree.heading("title", text="Project Title / Name")
        self.tree.heading("category", text="Categories")
        self.tree.heading("type", text="Display Mode")
        self.tree.column("title", width=360, anchor="w")
        self.tree.column("category", width=140, anchor="center")
        self.tree.column("type", width=140, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1B1B22", foreground="#FFFFFF", fieldbackground="#1B1B22", rowheight=28)
        style.map("Treeview", background=[("selected", "#F59E0B")], foreground=[("selected", "#000000")])

        btn_box = tk.Frame(left_frame, bg="#141418")
        btn_box.pack(fill="x", padx=10, pady=10)

        btn_add = tk.Button(btn_box, text="+ Add New Project", bg="#22C55E", fg="#FFFFFF", font=("Arial", 9, "bold"), bd=0, padx=10, pady=5, cursor="hand2", command=self.add_project_dialog)
        btn_add.pack(side="left", padx=5)

        btn_edit = tk.Button(btn_box, text="Edit Selected", bg="#3B82F6", fg="#FFFFFF", font=("Arial", 9, "bold"), bd=0, padx=10, pady=5, cursor="hand2", command=self.edit_project_dialog)
        btn_edit.pack(side="left", padx=5)

        btn_up = tk.Button(btn_box, text="▲ Move Up", bg="#374151", fg="#FFFFFF", font=("Arial", 9, "bold"), bd=0, padx=10, pady=5, cursor="hand2", command=self.move_up)
        btn_up.pack(side="left", padx=5)

        btn_down = tk.Button(btn_box, text="▼ Move Down", bg="#374151", fg="#FFFFFF", font=("Arial", 9, "bold"), bd=0, padx=10, pady=5, cursor="hand2", command=self.move_down)
        btn_down.pack(side="left", padx=5)

        btn_del = tk.Button(btn_box, text="Delete", bg="#EF4444", fg="#FFFFFF", font=("Arial", 9, "bold"), bd=0, padx=10, pady=5, cursor="hand2", command=self.delete_project)
        btn_del.pack(side="right", padx=5)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in self.projects:
            p_type = p.get("type", "case_study")
            if p_type == "case_study":
                display_type = "Case Study Page"
            elif p_type == "visual_identity":
                display_type = "Visual Identity"
            else:
                display_type = f"Lightbox ({p.get('lightbox_media_type', 'image')})"

            title = p.get("title", p.get("id", "Untitled"))
            cats = p.get("category", ["identity"])
            cat_display = ", ".join(cats) if isinstance(cats, list) else str(cats)
            self.tree.insert("", "end", iid=p.get("id"), values=(title, cat_display, display_type))

    def move_up(self):
        sel = self.tree.selection()
        if not sel:
            return
        p_id = sel[0]
        idx = next((i for i, p in enumerate(self.projects) if p.get("id") == p_id), -1)
        if idx > 0:
            self.projects[idx], self.projects[idx - 1] = self.projects[idx - 1], self.projects[idx]
            save_data(self.projects)
            self.refresh_list()
            self.tree.selection_set(p_id)
            self.tree.see(p_id)

    def move_down(self):
        sel = self.tree.selection()
        if not sel:
            return
        p_id = sel[0]
        idx = next((i for i, p in enumerate(self.projects) if p.get("id") == p_id), -1)
        if idx != -1 and idx < len(self.projects) - 1:
            self.projects[idx], self.projects[idx + 1] = self.projects[idx + 1], self.projects[idx]
            save_data(self.projects)
            self.refresh_list()
            self.tree.selection_set(p_id)
            self.tree.see(p_id)

    def on_build(self):
        import subprocess

        # 1. Regenerate local HTML files
        if not build_website():
            return

        # 2. Automatically sync changes to GitHub
        try:
            # Stage modified and newly created files
            subprocess.run(["git", "add", "."], check=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            
            # Commit changes (ignores error if nothing new was edited)
            subprocess.run(["git", "commit", "-m", "Portfolio update via manager"], 
                           capture_output=True, 
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            
            # Push updates to your GitHub repository
            subprocess.run(["git", "push", "origin", "main"], check=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            
            messagebox.showinfo(
                "Success & Published! 🚀", 
                "Website built and pushed to GitHub successfully!\n\nYour live site will reflect the changes in about 30–60 seconds."
            )
        except subprocess.CalledProcessError as err:
            messagebox.showwarning(
                "Local Build OK (Sync Failed)", 
                f"HTML files updated locally, but Git push failed:\n{err}\n\nYou can still run 'git push' manually in the terminal."
            )
        except Exception as e:
            messagebox.showinfo(
                "Built Locally", 
                f"Website built locally, but auto-publish encountered an issue:\n{e}"
            )

    def delete_project(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a project to delete.")
            return
        p_id = sel[0]
        if messagebox.askyesno("Confirm", f"Delete project '{p_id}'?"):
            self.projects = [p for p in self.projects if p.get("id") != p_id]
            save_data(self.projects)
            self.refresh_list()

    def add_project_dialog(self):
        ProjectEditor(self.root, on_save=self.save_new_project)

    def edit_project_dialog(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a project to edit.")
            return
        p_id = sel[0]
        proj = next((p for p in self.projects if p.get("id") == p_id), None)
        if proj:
            ProjectEditor(self.root, project_data=proj, on_save=self.save_edited_project)

    def save_new_project(self, new_proj):
        self.projects.append(new_proj)
        save_data(self.projects)
        self.refresh_list()

    def save_edited_project(self, updated_proj):
        for i, p in enumerate(self.projects):
            if p.get("id") == updated_proj.get("id"):
                self.projects[i] = updated_proj
                break
        save_data(self.projects)
        self.refresh_list()

class ProjectEditor(tk.Toplevel):
    def __init__(self, parent, project_data=None, on_save=None):
        super().__init__(parent)
        self.title("Project Details Editor")
        self.geometry("660x820")
        self.configure(bg="#141418")
        self.on_save = on_save
        self.project_data = project_data or {}

        self.create_form()

    def create_form(self):
        canvas = tk.Canvas(self, bg="#141418", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#141418")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        def add_field(label_text, default_val=""):
            lbl = tk.Label(scrollable_frame, text=label_text, font=("Arial", 9, "bold"), fg="#F59E0B", bg="#141418")
            lbl.pack(anchor="w", pady=(8, 2))
            entry = tk.Entry(scrollable_frame, font=("Arial", 10), bg="#1B1B22", fg="#FFFFFF", insertbackground="#F59E0B", width=65)
            entry.insert(0, default_val)
            entry.pack(anchor="w")
            return entry

        self.ent_id = add_field("Unique ID / Slug (e.g. falfol-identity, palmier-dates):", self.project_data.get("id", ""))
        self.ent_title = add_field("Project Title:", self.project_data.get("title", ""))
        self.ent_subtitle = add_field("Subtitle / Brief Description:", self.project_data.get("subtitle", ""))

        self.ent_thumb = add_field("Card Cover Image URL (Cloudinary / Image link for the website grid):", self.project_data.get("thumbnail", ""))
        tk.Label(scrollable_frame, text="* Required: The image shown on the website grid card.", font=("Arial", 8), fg="#9CA3AF", bg="#141418").pack(anchor="w")

        # Categories
        tk.Label(scrollable_frame, text="Categories (Select all that apply):", font=("Arial", 9, "bold"), fg="#F59E0B", bg="#141418").pack(anchor="w", pady=(10, 2))

        cats_frame = tk.Frame(scrollable_frame, bg="#1B1B22", bd=1, relief="solid")
        cats_frame.pack(anchor="w", fill="x", pady=(2, 6))

        existing_cats = self.project_data.get("category", ["identity"])
        if isinstance(existing_cats, str):
            existing_cats = [existing_cats]

        self.cat_vars = {}
        category_options = [
            ("identity", "Visual Identity (هويات بصرية)"),
            ("social", "Social Media (سوشيال ميديا)"),
            ("motion", "Motion Graphics (موشن جرافيك)"),
            ("photo", "Photography (تصوير منتجات)"),
            ("prints", "Prints & Packaging (مطبوعات وتغليف)"),
            ("montage", "Montage & Reels (مونتاج وإعلانات)")
        ]

        for code, label in category_options:
            var = tk.BooleanVar(value=(code in existing_cats))
            self.cat_vars[code] = var
            chk = tk.Checkbutton(cats_frame, text=label, variable=var, font=("Arial", 9), bg="#1B1B22", fg="#FFFFFF", selectcolor="#0B0B0E", activebackground="#1B1B22", activeforeground="#F59E0B")
            chk.pack(anchor="w", padx=10, pady=3)

        # Display Mode: Supports Case Study, Lightbox, and Visual Identity
        tk.Label(scrollable_frame, text="Display Mode:", font=("Arial", 9, "bold"), fg="#F59E0B", bg="#141418").pack(anchor="w", pady=(8, 2))
        self.cb_type = ttk.Combobox(scrollable_frame, values=["case_study", "lightbox", "visual_identity"], state="readonly")
        self.cb_type.set(self.project_data.get("type", "visual_identity"))
        self.cb_type.pack(anchor="w")

        # Visual Identity Exclusives
        tk.Label(scrollable_frame, text="──────── Visual Identity & PDF Settings (If Mode = Visual Identity) ────────", font=("Arial", 9), fg="#6B7280", bg="#141418").pack(anchor="w", pady=15)
        self.ent_pdf = add_field("Brand Guidelines PDF URL (Cloudinary, Drive, or Direct PDF link):", self.project_data.get("pdf_url", ""))
        tk.Label(scrollable_frame, text="* Optional: Embeds an interactive PDF reader and a direct Download button.", font=("Arial", 8), fg="#9CA3AF", bg="#141418").pack(anchor="w")

        # Lightbox Settings
        tk.Label(scrollable_frame, text="──────── Lightbox Settings (If Mode = Lightbox) ────────", font=("Arial", 9), fg="#6B7280", bg="#141418").pack(anchor="w", pady=15)

        tk.Label(scrollable_frame, text="Lightbox Media Type:", font=("Arial", 9, "bold"), fg="#F59E0B", bg="#141418").pack(anchor="w", pady=(4, 2))
        self.cb_lightbox_type = ttk.Combobox(scrollable_frame, values=["video", "image"], state="readonly")
        self.cb_lightbox_type.set(self.project_data.get("lightbox_media_type", "video"))
        self.cb_lightbox_type.pack(anchor="w")

        self.ent_lightbox_url = add_field("Lightbox Video / Image URL to open on click (Vimeo, YouTube, or Image):", self.project_data.get("lightbox_media_url", ""))

        # Case Study Details
        tk.Label(scrollable_frame, text="──────── Case Study & Identity Page Metadata ────────", font=("Arial", 9), fg="#6B7280", bg="#141418").pack(anchor="w", pady=15)

        self.ent_client = add_field("Client Name:", self.project_data.get("client", "فلفول الشام"))
        self.ent_role = add_field("Role / Responsibility:", self.project_data.get("role", "Brand Identity & Art Direction"))
        self.ent_disciplines = add_field("Disciplines List:", self.project_data.get("disciplines", "Visual Identity, Typography, Packaging"))
        self.ent_year = add_field("Year:", self.project_data.get("year", "2026"))

        tk.Label(scrollable_frame, text="Project Overview / Concept Paragraph:", font=("Arial", 9, "bold"), fg="#F59E0B", bg="#141418").pack(anchor="w", pady=(8, 2))
        self.txt_overview = tk.Text(scrollable_frame, height=4, width=65, bg="#1B1B22", fg="#FFFFFF", insertbackground="#F59E0B")
        self.txt_overview.insert("1.0", self.project_data.get("overview", ""))
        self.txt_overview.pack(anchor="w")

        # Gallery Images (Line by line)
        tk.Label(scrollable_frame, text="Presentation Boards / Mockup Images (One URL per line):", font=("Arial", 9, "bold"), fg="#F59E0B", bg="#141418").pack(anchor="w", pady=(8, 2))
        self.txt_gallery = tk.Text(scrollable_frame, height=7, width=65, bg="#1B1B22", fg="#FFFFFF", insertbackground="#F59E0B")
        raw_gallery_items = self.project_data.get("gallery_images", [])
        clean_gallery_str = "\n".join([u.strip() for u in raw_gallery_items if u.strip().startswith("http")])
        self.txt_gallery.insert("1.0", clean_gallery_str)
        self.txt_gallery.pack(anchor="w")
        tk.Label(scrollable_frame, text="* In Visual Identity mode, these are displayed as high-impact presentation boards.", font=("Arial", 8), fg="#9CA3AF", bg="#141418").pack(anchor="w")

        # Case Study Videos
        tk.Label(scrollable_frame, text="Vimeo / YouTube Video Links (One link per line):", font=("Arial", 9, "bold"), fg="#F59E0B", bg="#141418").pack(anchor="w", pady=(8, 2))
        self.txt_video = tk.Text(scrollable_frame, height=3, width=65, bg="#1B1B22", fg="#FFFFFF", insertbackground="#F59E0B")
        self.txt_video.insert("1.0", self.project_data.get("video_embed_url", ""))
        self.txt_video.pack(anchor="w")

        btn_save = tk.Button(scrollable_frame, text="💾 Save Project", font=("Arial", 11, "bold"), bg="#F59E0B", fg="#000000", padx=20, pady=8, bd=0, cursor="hand2", command=self.save_and_close)
        btn_save.pack(anchor="w", pady=25)

    def save_and_close(self):
        slug = self.ent_id.get().strip()
        if not slug:
            messagebox.showwarning("Error", "ID / Slug is required (used for the URL).")
            return

        selected_cats = [code for code, var in self.cat_vars.items() if var.get()]
        if not selected_cats:
            selected_cats = ["identity"]

        raw_gallery_text = self.txt_gallery.get("1.0", "end-1c")
        gallery_urls = []
        for line in raw_gallery_text.splitlines():
            line = line.strip()
            if line.startswith("http://") or line.startswith("https://"):
                gallery_urls.append(line.rstrip(','))

        lb_type = self.cb_lightbox_type.get()
        lb_url = self.ent_lightbox_url.get().strip()
        if not lb_url:
            lb_url = self.ent_thumb.get().strip()

        thumb_val = self.ent_thumb.get().strip()
        if ("vimeo.com" in thumb_val or "youtube.com" in thumb_val) and not self.ent_lightbox_url.get().strip():
            lb_url = thumb_val
            lb_type = "video"
            thumb_val = ""

        raw_video_text = self.txt_video.get("1.0", "end-1c")
        video_lines = [v.strip().rstrip(',') for v in raw_video_text.splitlines() if v.strip()]
        video_field_val = "\n".join(video_lines)

        data = {
            "id": slug,
            "title": self.ent_title.get().strip(),
            "subtitle": self.ent_subtitle.get().strip(),
            "category": selected_cats,
            "type": self.cb_type.get(),
            "thumbnail": thumb_val,
            "lightbox_media_type": lb_type,
            "lightbox_media_url": lb_url,
            "pdf_url": self.ent_pdf.get().strip(),
            "client": self.ent_client.get().strip(),
            "role": self.ent_role.get().strip(),
            "disciplines": self.ent_disciplines.get().strip(),
            "year": self.ent_year.get().strip(),
            "overview": self.txt_overview.get("1.0", "end-1c").strip(),
            "deliverables": self.project_data.get("deliverables", ["Visual Identity", "Logo Construction", "Brand Guidelines"]),
            "gallery_images": gallery_urls,
            "video_embed_url": video_field_val
        }

        if self.on_save:
            self.on_save(data)
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioApp(root)
    root.mainloop()