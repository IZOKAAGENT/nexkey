# NEXKEY — AI Automation for Real Estate

> **La llave al futuro del real estate** | *The key to real estate's future*

---

## 🇪🇸 Español

**NEXKEY** es una empresa de automatización con agentes autónomos de IA especializada en el sector inmobiliario.

### Qué hacemos

- **Agente Captador+Calificador** — Responde leads en segundos, 24/7, vía WhatsApp, SMS y email
- **Agente de Seguimiento** — Nutre prospectos fríos hasta convertirlos en citas
- **Agente Agendador** — Coordina visitas automáticamente con calendario del broker

### Modelo

| Mercado | Montaje | Mensualidad |
|---------|---------|-------------|
| LatAm (ES) | $1,500 | $1,500/mes |
| EE.UU. (EN) | $3,000 | $3,000/mes |

### Arquitectura

- **Cerebro:** Hermes Agent + LM Studio (local GPU)
- **Hosting:** Vercel free tier
- **Operaciones:** Health checks, circuit breaker, retry, logging
- **Sin n8n / sin low-code** — arquitectura custom

---

## 🇬🇧 English

**NEXKEY** is an AI automation company building autonomous agents for the real estate industry.

### What we do

- **Lead Capture+Qualifier Agent** — Responds to leads in seconds, 24/7, via WhatsApp, SMS, and email
- **Follow-up Agent** — Nurtures cold prospects until they become appointments
- **Scheduler Agent** — Automatically coordinates property viewings with broker calendars

### Pricing

| Market | Setup Fee | Monthly Retainer |
|--------|-----------|------------------|
| LatAm (ES) | $1,500 | $1,500/mo |
| US (EN) | $3,000 | $3,000/mo |

### Architecture

- **Brain:** Hermes Agent + LM Studio (local GPU)
- **Hosting:** Vercel free tier
- **Operations:** Health checks, circuit breaker, retry, logging
- **No n8n / no low-code** — custom architecture

---

## Project Structure

```
nexkey/
├── agents/               # Agent modules
│   ├── router.py         # Intent router (ES/EN)
│   ├── lead_qualifier.py # Lead capture + qualification
│   ├── follow_up.py      # Prospect nurturing
│   ├── scheduler.py      # Appointment scheduling
│   └── prospector.py     # Dogfooding: self-prospecting agent
├── templates/            # Message templates
│   ├── es/               # Spanish templates
│   └── en/               # English templates
├── config/               # Configuration
│   ├── settings.yaml     # Main config
│   └── agents.yaml       # Agent-specific config
├── scripts/              # Operational scripts
│   ├── orchestrate.py    # Agent orchestrator
│   ├── deploy.sh         # Deployment script
│   ├── health_check.py   # Uptime monitoring
│   └── circuit_breaker.py# Failure handling
├── docs/                 # Documentation
│   ├── runbook.md        # Execution runbook
│   └── contracts/        # Legal templates
├── tests/                # Test suite
├── logs/                 # Runtime logs
└── assets/               # Branding, images
```

## Getting Started

```bash
# Setup
cd nexkey
python -m venv .venv
source .venv/bin/activate
uv pip install pyyaml

# Run orchestrator (dry-run)
python scripts/orchestrate.py --mode dry-run

# Deploy
bash scripts/deploy.sh
```

## 🌐 Links

- **GitHub:** https://github.com/IZOKAAGENT/nexkey
- **Landing:** https://nexkey.vercel.app (próximamente)

---

## License

Private — NEXKEY proprietary
