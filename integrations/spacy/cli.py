#!/usr/bin/env python3
"""
CLI wrapper for LinguisticLens nematocyst.
Allows invocation from TypeScript MCP tools.
"""

import json
import sys
from linguistic_lens import LinguisticLens

def main():
    """
    CLI entrypoint for LinguisticLens.

    Expects JSON input on stdin:
    {
        "text": "Text to analyze...",
        "model": "en_core_web_sm"  // Optional spaCy model
    }

    Outputs JSON to stdout:
    {
        "success": true,
        "reading": {...}
    }
    """
    try:
        # Read input
        input_data = json.loads(sys.stdin.read())

        text = input_data.get('text', '')
        model = input_data.get('model', 'en_core_web_sm')

        # Create lens and perceive
        lens = LinguisticLens(model=model)
        reading = lens.perceive(text)

        # Output result
        result = {
            'success': True,
            'reading': {
                'psi': reading.psi,
                'rho': reading.rho,
                'q': reading.q,
                'coherence': reading.coherence.to_dict(),
                'pos_pattern': reading.pos_pattern.value,
                'entity_count': reading.entity_count,
                'confidence': reading.confidence,
                'notes': reading.notes
            },
            'model': model
        }

        print(json.dumps(result, indent=2))
        return 0

    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }
        print(json.dumps(error_result, indent=2))
        return 1

if __name__ == '__main__':
    sys.exit(main())
