# Repository Instructions

These instructions apply to future agentic work in this repository.

## Change Discipline

- Make one logical change per PR.
- Keep changes small, reviewable, and easy to explain.
- Do not change the architecture without adding or updating an ADR in `docs/adr/`.
- Do not modify CI or security workflows without explicit human review.

## Security

- Never commit secrets, API keys, tokens, passwords, private keys, or production credentials.
- Never create a real `.env` file in git.
- Never add real PII, confidential documents, or customer data.
- Keep sample data synthetic and public-safe.
- Do not bake secrets into Docker images.

## Testing And Quality

- Tests are required for behavior changes.
- Documentation updates are required for user-facing or architectural changes.
- Run `python -m ruff check .`, `python -m ruff format --check .`, `python -m mypy src scripts tests`, and `python -m pytest` before opening a PR.
- Tests must run without external API keys or paid services.

## Architecture Preferences

- Prefer clear, maintainable code over clever abstractions.
- Keep mock providers deterministic.
- Keep paid provider usage optional and environment-gated.
- Preserve citations, retrieved context, guardrail decisions, and traceability in query responses.
- Do not weaken refusal behavior for unsupported or insufficient-context questions.

## Documentation

- Keep `README.md` and `README.es.md` aligned for major changes.
- Update `docs/security.md` when secret handling or threat assumptions change.
- Update `docs/cost-control.md` when provider behavior or deployment assumptions change.
- Update `docs/evaluation.md` when metrics or eval datasets change.
