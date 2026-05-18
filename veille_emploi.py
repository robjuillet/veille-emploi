import os
import json
import hashlib
import smtplib
import requests
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Configuration ────────────────────────────────────────────────
RECIPIENT_EMAIL  = "robjuillet@gmail.com"
SENDER_EMAIL     = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD  = os.environ["SENDER_PASSWORD"]
ANTHROPIC_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")  # optionnel
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
Il surveille déjà : Cafeyn, Deezer, Dailymotion, Molotov, Acast, Spotify, Netflix, Disney+, Paramount+,
TF1, M6, France Télévisions, Canal+, Radio France, arte, Telerama, Les Inrockuptibles, Society, Brut,
Konbini, Loopsider, Usbek & Rica, Prisma Media, Reworld Media, Mediawan, Newen Studios, Gaumont, UGC,
SND Films, mk2, Gaîté Lyrique, La Villette, Philharmonie de Paris, Lafayette Anticipations,
Flammarion, Actes Sud, Gallimard, Combat, Equativ, Teads, Ogury, Poool, Welcome to the Jungle,
Scoop.it, Twipe.
"""

COMPANIES = [
    # ── Streaming & plateformes ──────────────────────────────────
    {"name": "Cafeyn",               "cat": "Streaming & plateformes", "url": "https://careers.cafeyn.co/jobs"},
    {"name": "Deezer",               "cat": "Streaming & plateformes", "url": "https://www.deezerjobs.com/fr/offres/"},
    {"name": "Dailymotion",          "cat": "Streaming & plateformes", "url": "https://careers.dailymotion.com/jobs/"},
    {"name": "Molotov",              "cat": "Streaming & plateformes", "url": "https://molotov-tv.welcomekit.co/"},
    {"name": "Acast",                "cat": "Streaming & plateformes", "url": "https://careers.acast.com/jobs"},
    {"name": "Spotify",              "cat": "Streaming & plateformes", "url": "https://www.lifeatspotify.com/jobs?l=Paris"},
    {"name": "Netflix",              "cat": "Streaming & plateformes", "url": "https://explore.jobs.netflix.net/careers?query=%2A&location=Paris%2C%20IDF%2C%20France&pid=790315756419&domain=netflix.com&sort_by=relevance"},
    {"name": "Disney+",              "cat": "Streaming & plateformes", "url": "https://jobs.disneycareers.com/search-jobs/Paris"},
    {"name": "Paramount+",           "cat": "Streaming & plateformes", "url": "https://careers.paramount.com/search/?createNewAlert=false&q=&locationsearch=France&optionsFacetsDD_customfield1=&optionsFacetsDD_customfield2=&optionsFacetsDD_customfield3="},
    # ── Médias & presse ──────────────────────────────────────────
    {"name": "TF1 Group",            "cat": "Médias & presse",         "url": "https://carrieres.groupe-tf1.fr/go/Toutes-nos-offres/4293001/"},
    {"name": "M6 Group",             "cat": "Médias & presse",         "url": "https://www.groupem6.fr/offres/?_contract_type=cdi"},
    {"name": "France Télévisions",   "cat": "Médias & presse",         "url": "https://recrutement.francetelevisions.fr/search/?createNewAlert=false&q=&optionsFacetsDD_shifttype=&optionsFacetsDD_department=&optionsFacetsDD_city="},
    {"name": "Canal+",               "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/canal-group/jobs"},
    {"name": "Radio France",         "cat": "Médias & presse",         "url": "https://radiofrance-recrute.talent-soft.com/offre-de-emploi/liste-toutes-offres.aspx"},
    {"name": "arte",                 "cat": "Médias & presse",         "url": "https://emploi.artefrance.fr/offre"},
    {"name": "Telerama",             "cat": "Médias & presse",         "url": "https://recrutement.lemonde.fr"},
    {"name": "Brut",                 "cat": "Médias & presse",         "url": "https://brutfrance.teamtailor.com/jobs"},
    {"name": "Konbini",              "cat": "Médias & presse",         "url": "https://konbini.welcomekit.co/"},
    {"name": "Loopsider",            "cat": "Médias & presse",         "url": "https://www.welcometothejungle.com/fr/companies/loopsider/jobs"},
    {"name": "Usbek & Rica",         "cat": "Médias & presse",         "url": "https://jobs.makesense.org/fr/projects/usbek-rica-1622"},
    {"name": "Prisma Media",         "cat": "Médias & presse",         "url": "https://emploi.prismamedia.com/jobs?split_view=true&query=&employment_type=contract"},
    {"name": "Reworld Media",        "cat": "Médias & presse",         "url": "https://careers.werecruit.io/fr/reworld-media?lieuList=92---arcueil%2C92---boulogne-billancourt&typeDeContratList=1#block-0a380d96-1bee-4330-925a-10a3c83212ee"},
    # ── Cinéma & production ──────────────────────────────────────
    {"name": "Mediawan",             "cat": "Cinéma & production",     "url": "https://career.mediawan.com/fr/annonces"},
    {"name": "Gaumont",              "cat": "Cinéma & production",     "url": "https://www.gaumont.com/fr/valeurs-engagement-rse-rh"},
    {"name": "UGC",                  "cat": "Cinéma & production",     "url": "https://www.ugc.fr/metiers-recrutement.html"},
    {"name": "SND Films",            "cat": "Cinéma & production",     "url": "https://www.recrutement.groupem6.fr/offre-de-emploi/liste-offres.aspx"},
    {"name": "mk2",                  "cat": "Cinéma & production",     "url": "https://mk2pro.com/nous-rejoindre/"},
    # ── Culture & institutions ───────────────────────────────────
    {"name": "Gaîté Lyrique",        "cat": "Culture & institutions",  "url": "https://www.gaite-lyrique.net/rejoindre-l-equipe/#toutes-les-offres"},
    {"name": "La Villette",          "cat": "Culture & institutions",  "url": "https://lavillette.taleez.com/"},
    {"name": "Philharmonie de Paris","cat": "Culture & institutions",  "url": "https://philharmoniedeparis.fr/fr/informations-pratiques/recrutement"},
    {"name": "Lafayette Anticipations","cat": "Culture & institutions","url": "https://www.lafayetteanticipations.com/fr/recrutement"},
    # ── Édition ──────────────────────────────────────────────────
    {"name": "Flammarion",           "cat": "Édition",                 "url": "https://madrigall.nous-recrutons.fr/offres-emploi/"},
    # ── Adtech / médiatech ───────────────────────────────────────
    {"name": "Equativ",              "cat": "Adtech / médiatech",      "url": "https://equativ.com/careers/"},
    {"name": "Teads",                "cat": "Adtech / médiatech",      "url": "https://www.teads.com/fr/teads-careers/job-openings/?_job-locations=paris"},
    {"name": "Ogury",                "cat": "Adtech / médiatech",      "url": "https://ogury.com/careers/"},
    {"name": "Scoop.it",             "cat": "Adtech / médiatech",      "url": "https://www.scoop-it.fr/recrutement/"},
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

    print("→ Génération des recommandations...")
    recommandations = get_recommandations()

    nb_changed = len([r for r in results if r["status"] == "changed"])
    html_body  = build_email_html(results, recommandations, today)
    send_email(html_body, today, nb_changed)
    print(f"\n✓ Email envoyé — {nb_changed} changement(s), {len(recommandations)} recommandation(s)")

if __name__ == "__main__":
    main()
