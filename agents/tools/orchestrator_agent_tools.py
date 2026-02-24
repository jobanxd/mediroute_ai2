"""Orchestrator agent tools definitions."""

CALL_CLASSIFICATION_AGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "call_classification_agent",
        "description": (
            "Use this tool when the patient has provided their symptoms or emergency condition, "
            "their current location, preffered hospital, and their insurance provider. "
            "This will route the request to the intake agent for structured extraction "
            "and hospital matching."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The full original message from the patient describing "
                        "their emergency, location, and insurance provider."
                    )
                },
                "purpose": {
                    "type": "string",
                    "description": (
                        "Brief reason why this is being routed to the intake agent "
                        "(e.g. 'Patient described cardiac symptoms with location "
                        "and insurance info provided')."
                    )
                }
            },
            "required": ["query", "purpose"]
        }
    }
}


CALL_LOA_AGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "call_loa_agent",
        "description": (
            "Use this tool when the patient has confirmed or chosen a specific hospital "
            "they want to be admitted to. This will route the request to the LOA agent "
            "to initiate the Letter of Authorization process with the chosen hospital "
            "and the patient's insurance provider."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The full context of the conversation including the patient's "
                        "emergency details, insurance provider, and their chosen hospital."
                    )
                },
                "chosen_hospital": {
                    "type": "string",
                    "description": (
                        "The name of the hospital the patient has chosen "
                        "(e.g. 'St. Luke's Medical Center')."
                    )
                },
                "purpose": {
                    "type": "string",
                    "description": (
                        "Brief reason why this is being routed to the LOA agent "
                        "(e.g. 'Patient confirmed St. Luke's as their preferred hospital, "
                        "LOA process can begin')."
                    )
                }
            },
            "required": ["query", "chosen_hospital", "purpose"]
        }
    }
}