#!/usr/bin/env python3
"""
CLI wrapper for WisdomLens nematocyst.
Allows invocation from TypeScript MCP tools.
"""

import json
import sys
from typing import List
from wisdom_lens import WisdomLens, MathematicalContext

def main():
    """
    CLI entrypoint for WisdomLens.

    Expects JSON input on stdin:
    {
        "data": [1.2, 3.4, 5.6, ...],
        "calibration": "practical|academic|indigenous_oral|contemplative",
        "context": "general|financial|scientific|statistical|communication"
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

        data = input_data.get('data', [])
        calibration = input_data.get('calibration', 'practical')
        context_str = input_data.get('context', 'general')

        # Map context string to enum
        context_map = {
            'general': MathematicalContext.GENERAL,
            'financial': MathematicalContext.FINANCIAL,
            'scientific': MathematicalContext.SCIENTIFIC,
            'statistical': MathematicalContext.STATISTICAL,
            'communication': MathematicalContext.COMMUNICATION
        }
        context = context_map.get(context_str, MathematicalContext.GENERAL)

        # Create lens and perceive
        lens = WisdomLens(
            cultural_calibration=calibration,
            context=context
        )

        reading = lens.perceive_rigor(data, context)

        # Output result
        result = {
            'success': True,
            'reading': {
                'rho': reading.rho,
                'consistency': reading.consistency,
                'precision': reading.precision,
                'stability': reading.stability,
                'convergence': reading.convergence,
                'confidence': reading.confidence,
                'context': reading.context.value,
                'notes': reading.notes
            },
            'calibration': calibration
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
