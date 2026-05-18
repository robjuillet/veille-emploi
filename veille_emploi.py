import os
import json
import hashlib
import smtplib
import requests
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

# ── Configuration ────────────────────────────────────────────────
RECIPIENT_EMAIL = "robjuillet@gmail.com"
SENDER_EMAIL    = os.environ["SENDER_EMAIL"]   # ton Gmail expéditeur
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"] # mot de passe d'application Gmail
CACHE_FILE      = "jobs_cache.json"

KEYWORDS = [
    "stratégie", "strategie", "strategy",
    "développement", "developpement", "development",
    "business development", "bizdev",
    "produit", "product",
    "contenu", "contenus", "content", "editorial", "éditorial",
    "partenariats", "partnership",
    "audience", "plateforme", "platform",
    "médias", "medias", "media",
    "streaming", "numérique", "digital",
]

COMPANIES = [
    # ── Streaming & plateformes ──────────────────────────────────
    {"name": "Cafeyn",          "url": "https://www.welcometothejungle.com/fr/companies/cafeyn/jobs"},
    {"name": "Deezer",          "url": "https://www.deezer.com/fr/company/jobs"},
    {"name": "Dailymotion",     "url": "https://www.dailymotion.com/fr/careers"},
    {"name": "Molotov",         "url": "https://www.welcometothejungle.com/fr/companies/molotov/jobs"},
    {"name": "Acast",           "url": "https://www.acast.com/en/jobs"},
    {"name": "Spotify",         "url": "https://www.lifeatspotify.com/jobs"},
    {"name": "Netflix",         "url": "https://jobs.netflix.com/search?location=Paris%2C%20France"},
    {"name": "Disney+",         "url": "https://jobs.disneycareers.com/search-jobs/Paris"},
    {"name": "Paramount+",      "url": "https://careers.paramount.com/search-jobs/Paris"},
    # ── Médias & presse ──────────────────────────────────────────
    {"name": "TF1 Group",       "url": "https://careers.tf1pub.fr"},
    {"name": "M6 Group",        "url": "https://www.groupem6.fr/rejoignez-nous.html"},
    {"name": "France Télévisions","url": "https://www.francetelevisions.fr/groupe/nous-rejoindre"},
    {"name": "Canal+",          "url": "https://www.canalplus.com/nous-rejoindre/"},
    {"name": "Radio France",    "url": "https://www.radiofrance.fr/nous-rejoindre"},
    {"name": "arte",            "url": "https://www.arte.tv/fr/corporate/emplois/"},
    {"name": "Telerama",        "url": "https://recrutement.lemonde.fr"},
    {"name": "Les Inrockuptibles","url": "https://www.welcometothejungle.com/fr/companies/les-inrockuptibles/jobs"},
    {"name": "Society / SoPress","url": "https://www.welcometothejungle.com/fr/companies/society/jobs"},
    {"name": "Brut",            "url": "https://www.welcometothejungle.com/fr/companies/brut/jobs"},
    {"name": "Konbini",         "url": "https://www.welcometothejungle.com/fr/companies/konbini/jobs"},
    {"name": "Loopsider",       "url": "https://www.welcometothejungle.com/fr/companies/loopsider/jobs"},
    {"name": "Usbek & Rica",    "url": "https://usbeketrica.com/fr/jobs"},
    {"name": "Prisma Media",    "url": "https://www.prismamedia.com/fr/carrieres"},
    {"name": "Reworld Media",   "url": "https://www.reworldmedia.com/fr/recrutement"},
    # ── Cinéma & production ──────────────────────────────────────
    {"name": "Mediawan",        "url": "https://www.mediawan.fr/nous-rejoindre"},
    {"name": "Newen Studios",   "url": "https://www.newen.tv/jobs"},
    {"name": "Gaumont",         "url": "https://www.gaumont.com/fr/offres-emploi/"},
    {"name": "UGC",             "url": "https://www.ugc.fr/recrutement.html"},
    {"name": "SND Films",       "url": "https://www.snd-films.com"},
    {"name": "mk2",             "url": "https://www.mk2.com/fr/jobs"},
    # ── Culture & institutions ───────────────────────────────────
    {"name": "Gaîté Lyrique",   "url": "https://gaite-lyrique.net/la-gaite/recrutement"},
    {"name": "La Villette",     "url": "https://lavillette.com/la-villette/recrutement"},
    {"name": "Philharmonie de Paris","url": "https://philharmoniedeparis.fr/fr/la-philharmonie/recrutement"},
    {"name": "Lafayette Anticipations","url": "https://www.lafayetteanticipations.com/fr/fondation"},
    # ── Édition ──────────────────────────────────────────────────
    {"name": "Flammarion",      "url": "https://www.flammarion.com/recrutement"},
    {"name": "Actes Sud",       "url": "https://www.actes-sud.fr/recrutement"},
    {"name": "Gallimard",       "url": "https://www.gallimard.fr/Gallimard/Groupe-Gallimard/Emplois-et-stages"},
    {"name": "Combat",          "url": "https://www.welcometothejungle.com/fr/companies/combat/jobs"},
    # ── Adtech / médiatech ───────────────────────────────────────
    {"name": "Equativ",         "url": "https://equativ.com/careers/"},
    {"name": "Teads",           "url": "https://www.teads.com/careers/"},
    {"name": "Ogury",           "url": "https://ogury.com/careers/"},
    {"name": "Poool",           "url": "https://www.welcometothejungle.com/fr/companies/poool/jobs"},
    {"name": "Welcome to the Jungle","url": "https://www.welcometothejungle.com/fr/companies/welcome-to-the-jungle/jobs"},
    {"name": "Scoop.it",        "url": "https://www.welcometothejungle.com/fr/companies/scoopit/jobs"},
    {"name": "Twipe",           "url": "https://www.twipemobile.com/careers/"},
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ── Cache ────────────────────────────────────────────────────────

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def page_hash(text):
    return hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()

# ── Scraping ─────────────────────────────────────────────────────

def fetch_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        return None

def extract_jobs(html, company_name):
    """
    Extrait les intitulés de postes qui contiennent au moins un mot-clé.
    Retourne une liste de strings.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Supprime scripts et styles
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text_blocks = []
    # Cherche les éléments susceptibles de contenir des titres de postes
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "li", "a", "span", "p"]):
        t = tag.get_text(strip=True)
        if 10 < len(t) < 120:  # filtre longueur pertinente
            text_blocks.append(t)

    # Déduplique
    seen = set()
    results = []
    for block in text_blocks:
        block_lower = block.lower()
        if block in seen:
            continue
        seen.add(block)
        if any(kw in block_lower for kw in KEYWORDS):
            results.append(block)

    return results[:15]  # max 15 résultats par entreprise

# ── Email ─────────────────────────────────────────────────────────

def build_email_html(results_by_company, new_companies, today):
    total_new = sum(len(v["new"]) for v in results_by_company.values())
    total_companies_with_news = len([v for v in results_by_company.values() if v["new"]])

    sections = []

    if total_new > 0:
        sections.append(f"""
        <div style="background:#f0f7ee;border-left:4px solid #3B6D11;padding:12px 16px;border-radius:4px;margin-bottom:24px;">
          <strong style="color:#27500A">🆕 {total_new} nouvelle(s) offre(s) détectée(s)</strong>
          sur {total_companies_with_news} entreprise(s)
        </div>""")

    for company, data in sorted(results_by_company.items()):
        new_jobs  = data["new"]
        all_jobs  = data["all"]
        url       = data["url"]
        is_new_co = company in new_companies

        if not all_jobs and not is_new_co:
            badge = '<span style="color:#888;font-size:12px">— aucune offre détectée</span>'
        else:
            badge = ""

        new_html = ""
        if new_jobs:
            items = "".join(
                f'<li style="margin:4px 0;color:#27500A">✦ {j}</li>'
                for j in new_jobs
            )
            new_html = f'<ul style="margin:6px 0 0 0;padding-left:18px;list-style:none">{items}</ul>'

        other_html = ""
        other_jobs = [j for j in all_jobs if j not in new_jobs]
        if other_jobs:
            items = "".join(
                f'<li style="margin:3px 0;color:#555">· {j}</li>'
                for j in other_jobs
            )
            other_html = f'<ul style="margin:6px 0 0 0;padding-left:18px;list-style:none;font-size:13px">{items}</ul>'

        sections.append(f"""
        <div style="border:1px solid #e0e0e0;border-radius:8px;padding:14px 18px;margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
            <strong style="font-size:15px">{company}</strong>
            <a href="{url}" style="font-size:12px;color:#185FA5;text-decoration:none">→ Page carrières</a>
          </div>
          {badge}
          {new_html}
          {other_html}
        </div>""")

    body = "\n".join(sections)

    return f"""
    <html><body style="font-family:system-ui,sans-serif;max-width:680px;margin:auto;padding:24px;color:#222">
      <h2 style="font-size:20px;font-weight:600;margin-bottom:4px">Veille emploi — {today}</h2>
      <p style="color:#666;font-size:14px;margin-bottom:24px">
        Récap quotidien · {len(results_by_company)} entreprises surveillées
      </p>
      {body}
      <p style="margin-top:32px;font-size:12px;color:#aaa;border-top:1px solid #eee;padding-top:12px">
        Script de veille personnalisé · robjuillet@gmail.com
      </p>
    </body></html>"""

def send_email(html_body, today):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Veille emploi] Récap du {today}"
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

# ── Main ──────────────────────────────────────────────────────────

def main():
    today = date.today().strftime("%d/%m/%Y")
    cache = load_cache()
    new_cache = {}
    results_by_company = {}
    new_companies = set()

    for company in COMPANIES:
        name = company["name"]
        url  = company["url"]
        print(f"→ {name}...")

        html = fetch_page(url)
        if not html:
            print(f"   ⚠ Impossible d'accéder à {url}")
            continue

        current_hash = page_hash(html)
        previous_hash = cache.get(name, {}).get("hash")
        previous_jobs = cache.get(name, {}).get("jobs", [])

        jobs = extract_jobs(html, name)
        new_cache[name] = {"hash": current_hash, "jobs": jobs}

        if previous_hash is None:
            new_companies.add(name)
            new_jobs = jobs
        elif current_hash != previous_hash:
            new_jobs = [j for j in jobs if j not in previous_jobs]
        else:
            new_jobs = []

        results_by_company[name] = {
            "new": new_jobs,
            "all": jobs,
            "url": url,
        }

    save_cache(new_cache)

    html_body = build_email_html(results_by_company, new_companies, today)
    send_email(html_body, today)
    print(f"\n✓ Email envoyé à {RECIPIENT_EMAIL}")

if __name__ == "__main__":
    main()
