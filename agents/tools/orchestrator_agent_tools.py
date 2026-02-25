"""Orchestrator agent tools definitions."""

CALL_VERIFICATION_AGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "call_verification_agent",
        "description": (
            "Use this tool when the patient has provided ALL of the following: "
            "symptoms or emergency condition, current location, and "
            "preferred hospital (or explicitly stated they have none). "
            "This will verify the patient's insurance eligibility by looking up their record "
            "using their full name, then automatically route to the classification agent "
            "for emergency processing. The insurance provider will be automatically retrieved."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {
                    "type": "string",
                    "description": (
                        "The full name of the patient or policy holder "
                        "(e.g. 'Juan dela Cruz'). Used to look up their insurance record."
                    )
                },
                "query": {
                    "type": "string",
                    "description": (
                        "The full original message from the patient describing "
                        "their emergency, location, and preferred hospital. "
                        "This will be passed to the classification agent after verification."
                    )
                },
                "purpose": {
                    "type": "string",
                    "description": (
                        "Brief reason why this is being routed "
                        "(e.g. 'Patient Juan dela Cruz described cardiac symptoms in BGC, "
                        "all required info collected')."
                    )
                }
            },
            "required": ["patient_name", "query", "purpose"]
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