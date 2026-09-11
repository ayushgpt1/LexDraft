from typing import List, Optional
from pydantic import BaseModel, Field


class Respondent(BaseModel):
    number: int
    name: str


class Deponent(BaseModel):
    name: str
    designation: Optional[str] = None
    organisation: Optional[str] = None
    address: Optional[str] = None
    age: Optional[str] = None
    occupation: Optional[str] = None


class ReplyPoint(BaseModel):
    point_number: int
    move_type: str
    content: List[str]


class CaseInformation(BaseModel):
    document_type: str

    # Court and case
    court: str
    jurisdiction: str
    proceeding_type: str
    case_number: str
    year: int

    # Parties
    petitioner: str
    respondents: List[Respondent]
    answering_respondent_number: int

    # Deponent
    deponent: Deponent

    # Reply
    reply_points: List[ReplyPoint]

    # Prayer
    prayer: List[str]

    # Attestation
    verification_verb: str
    place: str
    date: str

    # Advocate
    advocate_firm: Optional[str] = None
    advocate_for: Optional[str] = None


class EvaluationCriterion(BaseModel):
    score: int = Field(ge=0, le=100)
    issues: List[str] = Field(default_factory=list)


class EvaluationReport(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    entity_accuracy: EvaluationCriterion
    completeness: EvaluationCriterion
    semantic_faithfulness: EvaluationCriterion
    hallucination: EvaluationCriterion
    template_fidelity: EvaluationCriterion
    overall_issues: List[str] = Field(default_factory=list)