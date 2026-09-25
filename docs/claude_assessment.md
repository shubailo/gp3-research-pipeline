## MedBuddy – Módosított megvalósítási terv

### Startup, ingyenes pilot fázis → skálázható éles rendszer

---

## 1. Stack összefoglaló

```
PILOT (ingyenes)                    ÉLES (later)
─────────────────────────────────────────────────
Frontend   → Vercel (statikus)      változatlan
Backend    → Render free tier       Render $7/hó
Adatbázis  → Supabase free          változatlan  
AI         → Gemini 2.0 Flash       Anthropic Claude
Auth       → Supabase Auth          + Azure AD SSO
```

---

## 2. Mappa- és fájlstruktúra

```
medbuddy/
│
├── frontend/                          # Next.js – Vercelre megy
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               # Landing / agent választó
│   │   │   ├── chat/[agentId]/
│   │   │   │   └── page.tsx           # Chat felület
│   │   │   └── dashboard/
│   │   │       └── page.tsx           # Korábbi sessionök
│   │   ├── components/
│   │   │   ├── AgentSelector.tsx
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── RubricPanel.tsx
│   │   │   └── SessionHistory.tsx
│   │   └── lib/
│   │       ├── api.ts                 # Backend hívások
│   │       └── supabase.ts            # Auth + session olvasás
│   └── .env.local
│       NEXT_PUBLIC_BACKEND_URL=...
│       NEXT_PUBLIC_SUPABASE_URL=...
│       NEXT_PUBLIC_SUPABASE_ANON_KEY=...
│
├── backend/                           # Express – Renderre megy
│   ├── agents/
│   │   ├── hegyi.json                 # Meglévő profil, kész
│   │   ├── garami.json                # Legenerálandó
│   │   └── _template.json             # Új kutató hozzáadásához
│   ├── src/
│   │   ├── index.ts                   # Express app belépési pont
│   │   ├── routes/
│   │   │   ├── chat.ts                # POST /api/chat
│   │   │   ├── score.ts               # POST /api/score
│   │   │   └── sessions.ts            # GET/POST /api/sessions
│   │   ├── services/
│   │   │   ├── ai_client.ts           # ← KULCSFONTOSSÁGÚ réteg
│   │   │   ├── agent_loader.ts        # JSON profilok betöltése
│   │   │   └── scorer.ts              # Rubrika logika
│   │   └── middleware/
│   │       ├── auth.ts                # Supabase JWT validálás
│   │       └── rate_limit.ts          # Napi limit / user
│   └── .env
│       AI_PROVIDER=gemini             # vagy 'anthropic'
│       GEMINI_API_KEY=...
│       ANTHROPIC_API_KEY=...          # üresen hagyható pilotban
│       SUPABASE_URL=...
│       SUPABASE_SERVICE_KEY=...
│
└── scripts/                           # Meglévő Python scriptek
    ├── hegyi_pubmed_scraper.py        # változatlan
    ├── hegyi_pattern_analyzer.py      # változatlan
    ├── garami_pubmed_scraper.py       # változatlan
    └── garami_pattern_analyzer.py     # változatlan
```

---

## 3. Az `ai_client.ts` – a legfontosabb fájl

Ez az egyetlen réteg, ami miatt a Gemini→Anthropic váltás egyetlen environment variable csere lesz, nem kódmódosítás.

```
AI_PROVIDER=gemini   →  Gemini 2.0 Flash (ingyenes)
AI_PROVIDER=anthropic →  Claude Sonnet (éles)
```

Mindkét provider ugyanazt az interfészt kapja: `{ systemPrompt, messages, contextAbstracts }` be, `string` ki. A többi kód nem tud róla, melyik AI fut alatta.

---

## 4. Agent JSON struktúra (egységesítve)

A meglévő `hegyi_agent_profile.json` gazdag, de két mezőt kell hozzáadni:

```json
{
  "id": "hegyi",
  "name": "Prof. Hegyi Péter",
  "title": "Transzlációs medicina · Pankreatológia",
  "avatar": "🔬",
  "active": true,

  "system_prompt": "...(meglévő, változatlan)...",

  "evaluation_dimensions": [
    {
      "key": "klinikai_relevancia",
      "label": "Klinikai relevancia",
      "max_score": 10,
      "description": "Van-e valós betegcsoport és mérhető hatás?"
    },
    {
      "key": "precizitas",
      "label": "Precizitás (PICO)",
      "max_score": 10,
      "description": "Population, Intervention, Comparison, Outcome definiálva?"
    },
    {
      "key": "translacionalitas",
      "label": "Transzlációs elhelyezés",
      "max_score": 10,
      "description": "T0–T4 skálán hol van, mi a következő lépés?"
    },
    {
      "key": "innovacio",
      "label": "Innováció",
      "max_score": 10,
      "description": "Mi az újdonság a meglévő irodalomhoz képest?"
    },
    {
      "key": "megvalosithatosag",
      "label": "Megvalósíthatóság",
      "max_score": 10,
      "description": "Elvégezhető 3–4 évben kellő tudományos szigorral?"
    }
  ],

  "context_abstracts": [
    "...(top 80 absztrakt szövege, prompt cache-hez)..."
  ],

  "starter_topics": [
    "Vizsgálni szeretném az akut pancreatitis korai...",
    "..."
  ]
}
```

Új kutató hozzáadása a rendszerhez = egy új JSON fájl az `agents/` mappában. Kód nem kell hozzá.

---

## 5. Adatbázis séma (Supabase)

```sql
-- Supabase Auth kezeli a users táblát, ezt egészítjük ki
create table profiles (
  id           uuid references auth.users primary key,
  email        text unique not null,
  institution  text,                    -- 'pte', 'semmelweis', egyéb
  role         text default 'student',  -- 'student' | 'admin'
  created_at   timestamp default now()
);

-- Munkamenetek
create table sessions (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid references profiles,
  agent_id     text not null,           -- 'hegyi' | 'garami'
  topic_title  text,                    -- első üzenetből auto-generált
  created_at   timestamp default now(),
  last_active  timestamp default now()
);

-- Üzenetek
create table messages (
  id           uuid primary key default gen_random_uuid(),
  session_id   uuid references sessions on delete cascade,
  role         text not null,           -- 'user' | 'assistant'
  content      text not null,
  created_at   timestamp default now()
);

-- Rubrika pontszámok (fejlődés követéséhez)
create table scores (
  id                    uuid primary key default gen_random_uuid(),
  session_id            uuid references sessions on delete cascade,
  iteration             int not null,
  klinikai_relevancia   int,
  precizitas            int,
  translacionalitas     int,
  innovacio             int,
  megvalosithatosag     int,
  total                 int,
  level                 text,
  created_at            timestamp default now()
);

-- Rate limiting táblája
create table daily_usage (
  user_id      uuid references profiles,
  date         date default current_date,
  message_count int default 0,
  primary key (user_id, date)
);
```

---

## 6. Auth stratégia – két fázis

**Pilot fázis:** Supabase email auth, middleware szinten domain ellenőrzéssel. Csak `@pte.hu`, `@semmelweis.hu`, vagy bármilyen email ha nyitottabb pilotot akarsz. Ez öt sor kód a backend middleware-ben.

**Éles fázis:** Microsoft Azure AD SSO – a PTE és Semmelweis egyaránt Azure-t használ. A NextAuth.js ezt natívan támogatja, a hallgatók az egyetemi jelszavukkal lépnek be, külön regisztráció nélkül. Ez IT egyeztetést igényel az intézménnyel, de technikailag nem bonyolult.

---

## 7. Rate limiting stratégia

Ingyenes AI tier védelméhez nélkülözhetetlen. A logika egyszerű: a `daily_usage` táblában számlálunk, és ha egy user eléri a napi limitet, 429-es hibát küld vissza a backend.

```
Pilot fázis:   20 üzenet/user/nap  (Gemini free tier védelme)
Éles fázis:    50 üzenet/user/nap  (Anthropic cost kontroll)
Admin userek:  korlátlan
```

---

## 8. Deployment – lépésről lépésre

**1. Supabase setup (30 perc)**
Új projekt létrehozása EU West régióban. SQL séma futtatása. Auth beállítás: email megerősítés bekapcsolva, opcionálisan domain whitelist. A service key és anon key kimásolása `.env` fájlokba.

**2. Backend – Render (20 perc)**
GitHub repóhoz kötött új Web Service. Build command: `npm install && npm run build`. Start command: `npm start`. Environment variables beállítása a Render dashboardon. Ingyenes tieren elindul, de az első kérés 30-60 másodpercet várhat (sleep mód) – ez pilotban elfogadható.

**3. Frontend – Vercel (10 perc)**
Ugyanaz a GitHub repó, `frontend/` mappa mint root. Environment variables: backend URL, Supabase kulcsok. Automatikus deploy minden `git push`-ra.

**4. Domain (opcionális, IT kérés)**
`medbuddy.pte.hu` CNAME rekord a Vercel deployment URL-re. Ez intézményi IT kérés, de nem technikai akadály.

---

## 9. Fejlesztési fázisok

**1. fázis – Pilot (3-4 hét, teljesen ingyenes)**

Az MVP tartalmazza: működő chat Hegyi és Garami ágensekkel, email regisztráció, session mentés, élő rubrika, rate limiting. Célcsoport: 10-15 önként jelentkező PhD hallgató PTE-ről. A cél visszajelzés gyűjtése, nem tökéletesség.

**2. fázis – Visszajelzés alapján (1-2 hónap)**

A pilot tapasztalatai alapján: UI finomítás, esetleg új kutató ágens hozzáadása, PDF export funkció a témavezetőnek, admin dashboard az intézménynek. Ebben a fázisban érdemes Render fizetős tierre váltani ($7/hó) hogy megszűnjön a sleep mód.

**3. fázis – Éles (folyamatos)**

Anthropic API bekapcsolása (environment variable csere), Azure AD SSO integráció, esetleg RAG visszahozása ha teljes cikkszövegeket is be akarnak vonni. Marketing: más magyar orvosi egyetemek megkeresése.

---

## 10. Költségek fázisok szerint

| | Pilot | Növekedés | Éles |
|---|---|---|---|
| Frontend (Vercel) | $0 | $0 | $0–20 |
| Backend (Render) | $0 | $7/hó | $7–25/hó |
| Adatbázis (Supabase) | $0 | $0 | $0–25/hó |
| AI (Gemini→Anthropic) | $0 | $10–30/hó | $50–150/hó |
| **Összesen** | **$0** | **$17–37/hó** | **$57–200/hó** |

Az Anthropic prompt caching bekapcsolásával az éles AI cost 60-70%-kal csökkenthető, mert az agent profilok és a statikus absztraktkontextus csak egyszer kerül számlázásra.

---

## 11. A legfontosabb dolog, amit most kell megcsinálni

Mielőtt egyetlen sor kódot írsz, a `garami_agent_profile.json`-t kell legenerálni – futtasd a meglévő `garami_pattern_analyzer.py` scriptet. Ez a tartalom a rendszer lelke, és ha ez gyenge, a legjobb tech stack sem segít. A Hegyi-profil már kész és kiváló minőségű – a Garami-profil ugyanolyan szintű legyen mielőtt az app elindul.