import os
import json
import hashlib
import smtplib
import requests
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Configuration ────────────────────────────────────────────────
RECIPIENT_EMAIL = "robjuillet@gmail.com"
SENDER_EMAIL    = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]
CACHE_FILE      = "jobs_cache.json"

COMPANIES = [
    # ── Streaming & plateformes ──────────────────────────────────
    {"name": "Cafeyn",               "cat": "Streaming & plateformes", "url": "https://www.welcometothejungle.com/fr/companies/cafeyn/jobs"},
    {"name": "Deezer",               "cat": "Streaming & plateformes", "url": "https://www.deezer.com/fr/company/jobs"},
    {"name": "Dailymotion",          "cat": "Streaming & plateformes", "url": "https://www.dailymotion.com/fr/careers"},
    {"name": "Molotov",              "cat": "Streaming & plateformes", "url": "https://www.welcometothejungle.com/fr/companies/molotov/jobs"},
    {"name": "Acast",                "cat": "Streaming & plateformes", "url": "https://www.acast.com/en/jobs"},
    {"name": "Spotify",              "cat": "Streaming & plateformes", "url": "https://www.lifeatspotify.com/jobs"},
    {"name": "Netflix",              "cat": "Streaming & plateformes", "url": "https://jobs.netflix.com/search?location=Paris%2C%20France"},
    {"name": "Disney+",              "cat": "Streaming & plateformes", "url": "https://jobs.disneycareers.com/search-jobs/Paris"},
    {"name": "Paramount+",           "cat": "Streaming & plateformes", "url": "https://careers.paramount.com/search-jobs/Paris"},
    # ── Médias & presse ──────────────────────────────────────────
    {"name": "TF1 Group",            "cat": "Médias & presse",         "url": "https://careers.tf1pub.fr"},
    {"name": "M6 Group",             "cat": "Médias & presse",         "url": "https://www.groupem6.fr/rejoignez-nous.html"},
    {"name": "France Télévisions",   "cat": "Médias & presse",         "url": "https://www.francetelevisions.fr/groupe/nous-rejoindre"},
    {"name": "Canal+",               "cat": "Médias & presse",         "url": "https://www.canalplus.com/nous-rejoindre/"},
    {"name": "Radio France",         "cat": "Médias & presse",         "url": "https://www.radiofrance.fr/nous-rejoindre"},
    {"name": "arte",                 "cat": "Médias & presse",         "url": "https://www.arte.tv/fr/corporate/emplois/"},
    {"name": "Telerama",             "cat": "Médias & presse",         "url": "https://recrutement.lemonde.fr"},
    {"name": "Les Inrockuptibles",   "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/les-inrockuptibles/jobs"},
    {"name": "Society / SoPress",    "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/society/jobs"},
    {"name": "Brut",                 "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/brut/jobs"},
    {"name": "Konbini",              "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/konbini/jobs"},
    {"name": "Loopsider",            "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/loopsider/jobs"},
    {"name": "Usbek & Rica",         "cat": "Médias & presse",         "url": "https://usbeketrica.com/fr/jobs"},
    {"name": "Prisma Media",         "cat": "Médias & presse",         "url": "https://www.prismamedia.com/fr/carrieres"},
    {"name": "Reworld Media",        "cat": "Médias & presse",         "url": "https://www.reworldmedia.com/fr/recrutement"},
    # ── Cinéma & production ──────────────────────────────────────
    {"name": "Mediawan",             "cat": "Cinéma & production",     "url": "https://www.mediawan.fr/nous-rejoindre"},
    {"name": "Newen Studios",        "cat": "Cinéma & production",     "url": "https://www.newen.tv/jobs"},
    {"name": "Gaumont",              "cat": "Cinéma & production",     "url": "https://www.gaumont.com/fr/offres-emploi/"},
    {"name": "UGC",                  "cat": "Cinéma & production",     "url": "https://www.ugc.fr/recrutement.html"},
    {"name": "SND Films",            "cat": "Cinéma & production",     "url": "https://www.snd-films.com"},
    {"name": "mk2",                  "cat": "Cinéma & production",     "url": "https://www.mk2.com/fr/jobs"},
    # ── Culture & institutions ───────────────────────────────────
    {"name": "Gaîté Lyrique",        "cat": "Culture & institutions",  "url": "https://gaite-lyrique.net/la-gaite/recrutement"},
    {"name": "La Villette",          "cat": "Culture & institutions",  "url": "https://lavillette.com/la-villette/recrutement"},
    {"name": "Philharmonie de Paris","cat": "Culture & institutions",  "url": "https://philharmoniedeparis.fr/fr/la-philharmonie/recrutement"},
    {"name": "Lafayette Anticipations","cat": "Culture & institutions","url": "https://www.lafayetteanticipations.com/fr/fondation"},
    # ── Édition ──────────────────────────────────────────────────
    {"name": "Flammarion",           "cat": "Édition",                 "url": "https://www.flammarion.com/recrutement"},
    {"name": "Actes Sud",            "cat": "Édition",                 "url": "https://www.actes-sud.fr/recrutement"},
    {"name": "Gallimard",            "cat": "Édition",                 "url": "https://www.gallimard.fr/Gallimard/Groupe-Gallimard/Emplois-et-stages"},
    {"name": "Combat",               "cat": "Édition",                 "url": "https://www.welcometothejungle.com/fr/companies/combat/jobs"},
    # ── Adtech / médiatech ───────────────────────────────────────
    {"name": "Equativ",              "cat": "Adtech / médiatech",      "url": "https://equativ.com/careers/"},
    {"name": "Teads",                "cat": "Adtech / médiatech",      "url": "https://www.teads.com/careers/"},
    {"name": "Ogury",                "cat": "Adtech / médiatech",      "url": "https://ogury.com/careers/"},
    {"name": "Poool",                "cat": "Adtech / médiatech",      "url": "https://www.welcometothejungle.com/fr/companies/poool/jobs"},
    {"name": "Welcome to the Jungle","cat": "Adtech / médiatech",      "url": "https://www.welcometothejungle.com/fr/companies/welcome-to-the-jungle/jobs"},
    {"name": "Scoop.it",             "cat": "Adtech / médiatech",      "url": "https://www.welcometothejungle.com/fr/companies/scoopit/jobs"},
    {"name": "Twipe",                "cat": "Adtech / médiatech",      "url": "https://www.twipemobile.com/careers/"},
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

# ── Fetch ────────────────────────────────────────────────────────

def fetch_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception:
        return None

# ── Email ─────────────────────────────────────────────────────────

def build_email_html(results, today):
    changed   = [r for r in results if r["status"] == "changed"]
    unchanged = [r for r in results if r["status"] == "unchanged"]
    failed    = [r for r in results if r["status"] == "error"]

    if changed:
        banner = f"""
        <div style="background:#e8f5e2;border-left:4px solid #3B6D11;padding:12px 16px;border-radius:4px;margin-bottom:28px;">
          <strong style="color:#27500A">🆕 {len(changed)} page(s) modifiée(s) depuis hier</strong>
          — va vérifier, il y a peut-être de nouvelles offres !
        </div>"""
    else:
        banner = f"""
        <div style="background:#f5f5f5;border-left:4px solid #aaa;padding:12px 16px;border-radius:4px;margin-bottom:28px;">
          <span style="color:#555">Aucun changement détecté aujourd'hui sur les {len(unchanged)} pages surveillées.</span>
        </div>"""

    cats = {}
    for r in results:
        cats.setdefault(r["cat"], []).append(r)

    sections = []
    for cat, items in cats.items():
        rows = ""
        for r in items:
            if r["status"] == "changed":
                icon  = "🆕"
                color = "#27500A"
                bg    = "#f0f7ee"
                label = "page modifiée"
            elif r["status"] == "error":
                icon  = "⚠️"
                color = "#856404"
                bg    = "#fffbe6"
                label = "inaccessible"
            else:
                icon  = "✓"
                color = "#aaa"
                bg    = "transparent"
                label = "aucun changement"

            rows += f"""
            <tr>
              <td style="padding:9px 8px;background:{bg};border-radius:4px;border-bottom:1px solid #f0f0f0;">
                <span style="font-size:13px;font-weight:{'600' if r['status']=='changed' else '400'};color:#222">{icon} {r['name']}</span>
                <span style="font-size:11px;color:{color};margin-left:8px">{label}</span>
              </td>
              <td style="padding:9px 8px;text-align:right;border-bottom:1px solid #f0f0f0;white-space:nowrap;">
                <a href="{r['url']}" style="font-size:12px;color:#185FA5;text-decoration:none">→ Voir les offres</a>
              </td>
            </tr>"""

        sections.append(f"""
        <div style="margin-bottom:28px;">
          <p style="font-size:11px;font-weight:600;color:#999;text-transform:uppercase;letter-spacing:0.06em;margin:0 0 8px">{cat}</p>
          <table style="width:100%;border-collapse:collapse;">{rows}</table>
        </div>""")

    body = "\n".join(sections)
    failed_note = f"<p style='font-size:12px;color:#bbb;margin-top:8px'>⚠️ {len(failed)} site(s) inaccessible(s) : {', '.join(r['name'] for r in failed)}</p>" if failed else ""

    return f"""
    <html><body style="font-family:system-ui,sans-serif;max-width:660px;margin:auto;padding:28px 24px;color:#222;background:#fff">
      <h2 style="font-size:19px;font-weight:600;margin:0 0 4px">Veille emploi — {today}</h2>
      <p style="color:#999;font-size:13px;margin:0 0 24px">{len(results)} entreprises surveillées</p>
      {banner}
      {body}
      {failed_note}
      <p style="margin-top:32px;font-size:11px;color:#ddd;border-top:1px solid #f0f0f0;padding-top:12px">
        Veille automatique · robjuillet@gmail.com
      </p>
    </body></html>"""

def send_email(html_body, today, nb_changed):
    subject = f"[Veille emploi] {today}"
    if nb_changed:
        subject += f" — 🆕 {nb_changed} nouveauté(s)"
    else:
        subject += " — aucun changement"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
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
    results = []

    for company in COMPANIES:
        name = company["name"]
        url  = company["url"]
        cat  = company["cat"]
        print(f"→ {name}...")

        html = fetch_page(url)
        if not html:
            print(f"   ⚠ Inaccessible")
            results.append({"name": name, "cat": cat, "url": url, "status": "error"})
            new_cache[name] = cache.get(name, {})
            continue

        current_hash  = page_hash(html)
        previous_hash = cache.get(name, {}).get("hash")
        new_cache[name] = {"hash": current_hash}

        if previous_hash is None:
            status = "unchanged"
        elif current_hash != previous_hash:
            status = "changed"
        else:
            status = "unchanged"

        results.append({"name": name, "cat": cat, "url": url, "status": status})

    save_cache(new_cache)

    nb_changed = len([r for r in results if r["status"] == "changed"])
    html_body  = build_email_html(results, today)
    send_email(html_body, today, nb_changed)
    print(f"\n✓ Email envoyé — {nb_changed} changement(s) détecté(s)")

if __name__ == "__main__":
    main()
