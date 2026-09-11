from typing import List

from pydantic import BaseModel

from backend.models.schemas import (
    CaseInformation,
    EvaluationReport,
)
from backend.core.content_mapper import map_content
from backend.core.document_generator import build_affidavit_docx, extract_docx_text
from backend.validation.validators import (
    run_all_validations,
    calculate_deterministic_score,
)
from backend.core.document_generator import (
    build_affidavit_docx,
    extract_docx_text,
)

class GeneratedParagraph(BaseModel):
    paragraph_number: int
    content: str


class GeneratedParagraphs(BaseModel):
    paragraphs: List[GeneratedParagraph]


class FinalEvaluationReport(BaseModel):
    deterministic_score: float
    deterministic_checks: List[dict]
    llm_evaluation: EvaluationReport


class AffidavitOrchestrator:

    def __init__(
        self,
        extraction_agent,
        generation_agent,
        evaluation_agent
    ):
        self.extraction_agent = extraction_agent
        self.generation_agent = generation_agent
        self.evaluation_agent = evaluation_agent

    def run(
        self,
        case_text,
        reference_text,
        reference_rules,
        output_path
    ):
        # 1. Extract case information
        extraction_raw = self.extraction_agent.run(case_text)

        case_data = CaseInformation.model_validate_json(
            extraction_raw
        )

        # 2. Map extracted information
        mapped_content = map_content(case_data)

        # 3. Generate affidavit paragraphs
        generated_raw = self.generation_agent.run(
            reference_rules,
            mapped_content
        )

        generated_paragraphs = GeneratedParagraphs.model_validate_json(
            generated_raw
        )

        # 4. Build final DOCX affidavit
        build_affidavit_docx(
            case_data,
            generated_paragraphs,
            output_path
        )

        # 5. Extract generated document text
        generated_text = extract_docx_text(output_path)

        # 6. Run deterministic validation
        validation_results = run_all_validations(
            case_data,
            generated_text,
            generated_paragraphs
        )

        deterministic_score = calculate_deterministic_score(
            validation_results
        )

        # 7. Run LLM evaluation
        evaluation_raw = self.evaluation_agent.run(
            case_data=case_data,
            reference_text=reference_text,
            generated_text=generated_text
        )

        evaluation_report = EvaluationReport.model_validate_json(
            evaluation_raw
        )

        # 8. Build final evaluation report
        final_report = FinalEvaluationReport(
            deterministic_score=deterministic_score["score"],
            deterministic_checks=validation_results,
            llm_evaluation=evaluation_report
        )

        return {
            "case_data": case_data,
            "mapped_content": mapped_content,
            "generated_paragraphs": generated_paragraphs,
            "generated_text": generated_text,
            "validation_results": validation_results,
            "deterministic_score": deterministic_score,
            "evaluation_report": evaluation_report,
            "final_report": final_report,
            "output_path": output_path
        }