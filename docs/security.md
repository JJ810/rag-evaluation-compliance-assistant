# Security

## Secret Policy

Do not commit secrets. This includes:

- API keys;
- passwords;
- tokens;
- private keys;
- cloud credentials;
- production connection strings.

`.env` and `.env.*` are ignored by git. `.env.example` is safe and contains placeholders only.

## Threat Model

Primary V1 risks:

- accidental secret disclosure through prompts;
- prompt injection attempts inside user queries or future documents;
- unsupported answers presented as policy truth;
- missing or misleading citations;
- public repo exposure of credentials;
- dependency vulnerabilities;
- unexpected API cost if OpenAI mode is enabled.

## Prompt Injection Limitations

The deterministic guardrails block obvious prompt injection phrases and secret requests. This is not a complete defense.

Known limitations:

- attackers can phrase injection attempts indirectly;
- document-level prompt injection is not fully analyzed in V1;
- regex checks are brittle;
- downstream model behavior can vary by provider.

Recommended production additions:

- document sanitization;
- stricter system prompts;
- provider safety settings;
- content filters;
- allow-listed retrieval scopes;
- human review for sensitive outputs;
- red-team evaluation.

## API Key Handling

Use environment variables or a secret manager. Do not put API keys in:

- source code;
- Docker images;
- README examples;
- shell history where avoidable;
- issue comments;
- CI logs.

For GitHub Actions, use encrypted repository or environment secrets.

## Public Repo Safety Checklist

- [ ] No `.env` file committed.
- [ ] No real API keys in docs or tests.
- [ ] No production data or PII.
- [ ] Synthetic sample documents only.
- [ ] Tests pass in mock mode.
- [ ] CodeQL workflow enabled.
- [ ] Dependabot enabled.
- [ ] Docker image does not bake secrets.
- [ ] Evaluation report does not contain sensitive data.

## Credential Revocation Instructions

If a credential is accidentally exposed:

1. Revoke the credential in the provider console immediately.
2. Create a new credential with least privilege.
3. Remove the secret from git history if exposure reached commits.
4. Review CI logs, issues, pull requests, and screenshots.
5. Rotate any related credentials that may have been reachable.
6. Document the incident and corrective action.

## Least Privilege Assumptions

Optional OpenAI usage should use a key scoped to the smallest feasible project and budget. Hosted deployments should use separate credentials per environment.
