# Cost Control

## Default Cost

Default mode uses:

- mock embeddings;
- mock LLM responses;
- local JSON vector store;
- local SQLite traces.

Expected monthly cost in default mode: `$0`.

## Optional OpenAI Cost

OpenAI usage is opt-in through:

```text
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=...
```

Expected portfolio/demo usage should be low, but exact cost depends on provider pricing, model choice, token volume, and traffic.

## Max Tolerable Cost

For a public portfolio project, a reasonable max tolerable monthly cost is `$5-$20` unless there is a deliberate demo budget.

Recommended controls:

- use mock mode for CI and tests;
- keep OpenAI mode local/private;
- set provider-side monthly budgets;
- set alerts below the budget cap;
- avoid public unauthenticated OpenAI-backed endpoints;
- log provider mode and query volume.

## Free-Tier Assumptions

Do not assume a free tier will always exist. Treat any API-backed provider as potentially billable.

## Shutting Down Cloud Resources

This repo creates no cloud resources.

If future work adds cloud deployment:

1. stop running services;
2. delete unused containers or app services;
3. remove managed databases or vector stores;
4. disable scheduled jobs;
5. revoke deployment credentials;
6. check billing dashboards for residual usage.

## Cost Overrun Risks

- public endpoint receives unexpected traffic;
- evaluation loop calls paid models repeatedly;
- large documents increase embedding spend;
- traces or logs store more than expected;
- Docker deployment accidentally uses OpenAI mode;
- CI runs provider-backed tests.

V1 mitigates these risks by keeping mock mode as the default and requiring explicit environment configuration for paid providers.
