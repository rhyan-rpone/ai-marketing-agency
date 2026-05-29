from typing import TypedDict


class AgentState(TypedDict):

    question: str

    dataset_info: dict

    analysis_type: str

    schema_result: str

    analysis_result: str

    advanced_analysis: str

    final_response: str