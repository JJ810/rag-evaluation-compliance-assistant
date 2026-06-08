from __future__ import annotations

import json

from rag_compliance_assistant.api.dependencies import get_evaluation_service


def main() -> None:
    report = get_evaluation_service().run()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
