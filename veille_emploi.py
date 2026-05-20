import os
import json
import hashlib
import smtplib
import requests
import re
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

# ── Configuration ────────────────────────────────────────────────
RECIPIENT_EMAIL  = "robjuillet@gmail.com"
SENDER_EMAIL     = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD  = os.environ["SENDER_PASSWORD"]
ANTHROPIC_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")
CACHE_FILE       = "jobs_cache.json"

PROFIL = """
Robinson Juillet, 30 ans, Paris.
Après 5 ans de conseil en stratégie chez DEMAIN Conseil (missions médias, plateformes, streaming),
puis un poste de chef de projet numérique à la Ville de Paris, il cherche une nouvelle aventure professionnelle.
Ce qui l'anime : les plateformes de contenu, les nouveaux usages médias, le streaming, l'édition numérique,
les environnements culturellement vivants et ambitieux. Il aime les structures dynamiques où les sujets sont
exigeants et les interlocuteurs inspirants — grands groupes ou scale-ups, peu importe la taille.
Il fuit le public, le corporate sans âme et le retail.
Expériences clés : TF1+, M6+, arte, France Télévisions, Cité des Sciences.
Rôles recherchés : stratégie, business development, produit, contenus, partenariats, plateformes.
"""

COMPANIES = [
    # ── Streaming & plateformes ──────────────────────────────────
    {"name": "Cafeyn",               "cat": "Streaming & plateformes", "url": "https://careers.cafeyn.co/jobs"},
    {"name": "Deezer",               "cat": "Streaming & plateformes", "url": "https://www.deezerjobs.com/fr/offres/"},
    {"name": "Dailymotion",          "cat": "Streaming & plateformes", "url": "https://www.dailymotion.com/fr/careers"},
    {"name": "Molotov",              "cat": "Streaming & plateformes", "url": "https://molotov-tv.welcomekit.co/"},
    {"name": "Acast",                "cat": "Streaming & plateformes", "url": "https://careers.acast.com/jobs"},
    {"name": "Spotify",              "cat": "Streaming & plateformes", "url": "https://www.lifeatspotify.com/jobs?l=Paris"},
    {"name": "Netflix",              "cat": "Streaming & plateformes", "url": "https://jobs.netflix.com/search?location=Paris%2C%20France"},
    {"name": "Disney+",              "cat": "Streaming & plateformes", "url": "https://jobs.disneycareers.com/search-jobs/Paris"},
    {"name": "Paramount+",           "cat": "Streaming & plateformes", "url": "https://careers.paramount.com/search-jobs/Paris"},
    {"name": "Amazon Prime Video",   "cat": "Streaming & plateformes", "url": "https://www.amazon.jobs/fr/teams/prime-video"},
    # ── Médias & presse ──────────────────────────────────────────
    {"name": "TF1 Group",            "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/groupe-tf1/jobs"},
    {"name": "M6 Group",             "cat": "Médias & presse",         "url": "https://www.groupem6.fr/offres/"},
    {"name": "France Télévisions",   "cat": "Médias & presse",         "url": "https://recrutement.francetelevisions.fr/offre-de-emploi/liste-toutes-offres.aspx"},
    {"name": "Canal+",               "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/canal-group/jobs"},
    {"name": "Radio France",         "cat": "Médias & presse",         "url": "https://radiofrance-recrute.talent-soft.com/offre-de-emploi/liste-toutes-offres.aspx"},
    {"name": "arte",                 "cat": "Médias & presse",         "url": "https://emploi.artefrance.fr/offre"},
    {"name": "Telerama",             "cat": "Médias & presse",         "url": "https://recrutement.lemonde.fr"},
    {"name": "Les Inrockuptibles",   "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/les-inrockuptibles/jobs"},
    {"name": "Society / SoPress",    "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/society/jobs"},
    {"name": "Brut",                 "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/brut/jobs"},
    {"name": "Konbini",              "cat": "Médias & presse",         "url": "https://konbini.welcomekit.co/"},
    {"name": "Loopsider",            "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/loopsider/jobs"},
    {"name": "Usbek & Rica",         "cat": "Médias & presse",         "url": "https://usbeketrica.com/fr/jobs"},
    {"name": "Prisma Media",         "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/prisma-media/jobs"},
    {"name": "Reworld Media",        "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/reworld-media/jobs"},
    # ── Cinéma & production ──────────────────────────────────────
    {"name": "Mediawan",             "cat": "Cinéma & production",     "url": "https://www.welcometothejungle.com/fr/companies/mediawan/jobs"},
    {"name": "Newen Studios",        "cat": "Cinéma & production",     "url": "https://www.welcometothejungle.com/fr/companies/newen-studios/jobs"},
    {"name": "Gaumont",              "cat": "Cinéma & production",     "url": "https://www.gaumont.com/fr/valeurs-engagement-rse-rh"},
    {"name": "UGC",                  "cat": "Cinéma & production",     "url": "https://www.ugc.fr/metiers-recrutement.html"},
    {"name": "SND Films",            "cat": "Cinéma & production",     "url": "https://www.welcometothejungle.com/fr/companies/snd/jobs"},
    {"name": "mk2",                  "cat": "Cinéma & production",     "url": "https://www.welcometothejungle.com/fr/companies/mk2/jobs"},
    # ── Culture & institutions ───────────────────────────────────
    {"name": "Gaîté Lyrique",        "cat": "Culture & institutions",  "url": "https://gaite-lyrique.net/la-gaite/recrutement"},
    {"name": "La Villette",          "cat": "Culture & institutions",  "url": "https://lavillette.com/la-villette/recrutement"},
    {"name": "Philharmonie de Paris","cat": "Culture & institutions",  "url": "https://philharmoniedeparis.fr/fr/la-philharmonie/recrutement"},
    {"name": "Lafayette Anticipations","cat": "Culture & institutions","url": "https://www.lafayetteanticipations.com/fr/fondation"},
    # ── Édition ──────────────────────────────────────────────────
    {"name": "Flammarion",           "cat": "Édition",                 "url": "https://www.gallimard.fr/Gallimard/Groupe-Gallimard/Emplois-et-stages"},
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

# ── Extraction texte stable ───────────────────────────────────────

def extract_stable_text(html):
    """
    Extrait uniquement le texte visible de la page en supprimant :
    - tous les scripts et styles
    - les tokens, timestamps, IDs aléatoires
    - les espaces superflus
    Le résultat est stable d'une visite à l'autre même si la page
    contient des éléments dynamiques.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Supprimer scripts, styles, métadonnées
    for tag in soup(["script", "style", "meta", "link", "noscript", "iframe", "svg"]):
        tag.decompose()

    # Extraire le texte brut
    text = soup.get_text(separator=" ")

    # Nettoyer : supprimer les tokens hexadécimaux et UUIDs (très fréquents dans les SPA)
    text = re.sub(r'\b[a-f0-9]{8,}\b', '', text)
    text = re.sub(r'\b[A-Za-z0-9]{20,}\b', '', text)

    # Supprimer les nombres isolés (timestamps, compteurs)
    text = re.sub(r'\b\d{5,}\b', '', text)

    # Normaliser les espaces
    text = re.sub(r'\s+', ' ', text).strip()

    return hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()

# ── Fetch ────────────────────────────────────────────────────────

def fetch_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception:
        return None

# ── Recommandations via Claude (optionnel) ───────────────────────

def get_recommandations():
    if not ANTHROPIC_KEY:
        print("⚠ Pas de clé Anthropic — recommandations désactivées")
        return []

    prompt = f"""Tu es un conseiller en carrière spécialisé dans les médias, les plateformes digitales et la tech culturelle en France.

Voici le profil de la personne :
{PROFIL}

Ta mission : suggère 3 entreprises ou structures que cette personne ne surveille pas encore et qui pourraient l'intéresser.
Choisis des structures variées — mélange de grandes entreprises et de structures plus petites, françaises ou internationales présentes en France.
Pour chacune, donne :
- Le nom de la structure
- Une phrase courte sur ce qu'elle fait
- Une phrase courte expliquant pourquoi elle correspond au profil

Réponds UNIQUEMENT en JSON valide, sans texte autour, sans balises markdown, sous ce format exact :
[
  {{"nom": "Nom", "description": "Ce qu'elle fait.", "raison": "Pourquoi ça correspond."}},
  {{"nom": "Nom", "description": "Ce qu'elle fait.", "raison": "Pourquoi ça correspond."}},
  {{"nom": "Nom", "description": "Ce qu'elle fait.", "raison": "Pourquoi ça correspond."}}
]"""

    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        r.raise_for_status()
        text = r.json()["content"][0]["text"].strip()
        return json.loads(text)
    except Exception as e:
        print(f"⚠ Erreur recommandations : {e}")
        return []

# ── Email ─────────────────────────────────────────────────────────

def build_email_html(results, recommandations, today):
    changed  = [r for r in results if r["status"] == "changed"]
    unchanged= [r for r in results if r["status"] == "unchanged"]
    failed   = [r for r in results if r["status"] == "error"]

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
                icon = "🆕"; color = "#27500A"; bg = "#f0f7ee"; label = "page modifiée"; weight = "600"
            elif r["status"] == "error":
                icon = "⚠️"; color = "#856404"; bg = "#fffbe6"; label = "inaccessible"; weight = "400"
            else:
                icon = "✓"; color = "#aaa"; bg = "transparent"; label = "aucun changement"; weight = "400"

            rows += f"""
            <tr>
              <td style="padding:9px 8px;background:{bg};border-radius:4px;border-bottom:1px solid #f0f0f0;">
                <span style="font-size:13px;font-weight:{weight};color:#222">{icon} {r['name']}</span>
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

    if recommandations:
        reco_cards = ""
        for reco in recommandations:
            reco_cards += f"""
            <div style="border:1px solid #e8e8e8;border-radius:8px;padding:12px 16px;margin-bottom:10px;">
              <p style="font-size:14px;font-weight:600;color:#222;margin:0 0 4px">✦ {reco.get('nom', '')}</p>
              <p style="font-size:13px;color:#555;margin:0 0 4px">{reco.get('description', '')}</p>
              <p style="font-size:12px;color:#185FA5;margin:0">→ {reco.get('raison', '')}</p>
            </div>"""
        reco_section = f"""
        <div style="margin-top:36px;padding-top:24px;border-top:1px solid #eee;">
          <p style="font-size:11px;font-weight:600;color:#999;text-transform:uppercase;letter-spacing:0.06em;margin:0 0 16px">
            À explorer — suggestions du jour
          </p>
          {reco_cards}
        </div>"""
    else:
        reco_section = ""

    body = "\n".join(sections)
    failed_note = f"<p style='font-size:12px;color:#bbb;margin-top:8px'>⚠️ {len(failed)} site(s) inaccessible(s) : {', '.join(r['name'] for r in failed)}</p>" if failed else ""

    return f"""
    <html><body style="font-family:system-ui,sans-serif;max-width:660px;margin:auto;padding:28px 24px;color:#222;background:#fff">
      <h2 style="font-size:19px;font-weight:600;margin:0 0 4px">Veille emploi — {today}</h2>
      <p style="color:#999;font-size:13px;margin:0 0 24px">{len(results)} entreprises surveillées</p>
      {banner}
      {body}
      {failed_note}
      {reco_section}
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

        current_hash  = extract_stable_text(html)
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

    print("→ Génération des recommandations...")
    recommandations = get_recommandations()

    nb_changed = len([r for r in results if r["status"] == "changed"])
    html_body  = build_email_html(results, recommandations, today)
    send_email(html_body, today, nb_changed)
    print(f"\n✓ Email envoyé — {nb_changed} changement(s), {len(recommandations)} recommandation(s)")

if __name__ == "__main__":
    main()
