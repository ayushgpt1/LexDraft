import time
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

    def _emit(
        self,
        progress_callback,
        stage,
        status,
        message=None
    ):
        """
        Forward a progress event to the supplied callback.

        Events carry only the stage name, a status and an optional
        safe message; no API keys, stack traces or exception details
        are exposed.
        """

        if progress_callback is None:
            return

        event = {
            "stage": stage,
            "status": status
        }

        if message is not None:
            event["message"] = message

        progress_callback(event)

    def run(
        self,
        case_text,
        reference_text,
        reference_rules,
        output_path,
        progress_callback=None,
        reference_format_path=None,
        reference_sample_path=None
    ):
        # Total pipeline timer: starts before the first stage and
        # ends after the final evaluation stage.
        total_start = time.perf_counter()

        # 1. Extract case information
        start = time.perf_counter()

        self._emit(
            progress_callback,
            "extraction",
            "processing"
        )

        try:
            extraction_raw = self.extraction_agent.run(case_text)

            case_data = CaseInformation.model_validate_json(
                extraction_raw
            )
        except Exception:
            self._emit(
                progress_callback,
                "extraction",
                "error",
                message=(
                    "The extraction stage failed during generation."
                )
            )
            raise

        elapsed = time.perf_counter() - start
        print(f"[Timing] Extraction: {elapsed:.2f}s")

        self._emit(
            progress_callback,
            "extraction",
            "complete"
        )

        # Analyze format explained if a user-supplied path is provided
        # This allows the rules to be derived from the uploaded document
        # instead of using only the hardcoded defaults.
        if reference_format_path is not None:
            from backend.core.reference_analyzer import (
                analyze_format_explained,
                extract_pdf_text as extract_text
            )
            format_text = extract_text(reference_format_path)
            reference_rules = analyze_format_explained(format_text)

        # Analyze sample affidavit if a user-supplied path is provided
        # This allows pattern analysis from the uploaded sample
        sample_text = None
        if reference_sample_path is not None:
            from backend.core.reference_analyzer import (
                get_selected_sample_text,
                extract_pdf_text as extract_text
            )
            sample_text = get_selected_sample_text(reference_sample_path)
            if sample_text is None:
                sample_text = extract_text(reference_sample_path)

        # Pass sample info to generation if available (makes it available
        # for any future agent enhancements without breaking existing behavior)
        if sample_text:
            reference_rules['_sample_text_for_analysis'] = sample_text

        # 2. Map extracted information
        start = time.perf_counter()

        self._emit(
            progress_callback,
            "mapping",
            "processing"
        )

        try:
            mapped_content = map_content(case_data)
        except Exception:
            self._emit(
                progress_callback,
                "mapping",
                "error",
                message=(
                    "The mapping stage failed during generation."
                )
            )
            raise

        elapsed = time.perf_counter() - start
        print(f"[Timing] Mapping: {elapsed:.2f}s")

        self._emit(
            progress_callback,
            "mapping",
            "complete"
        )

        # 3. Generate affidavit paragraphs
        start = time.perf_counter()

        self._emit(
            progress_callback,
            "generation",
            "processing"
        )

        try:
            generated_raw = self.generation_agent.run(
                reference_rules,
                mapped_content
            )

            generated_paragraphs = GeneratedParagraphs.model_validate_json(
                generated_raw
            )
        except Exception:
            self._emit(
                progress_callback,
                "generation",
                "error",
                message=(
                    "The generation stage failed during generation."
                )
            )
            raise

        elapsed = time.perf_counter() - start
        print(f"[Timing] Generation: {elapsed:.2f}s")

        self._emit(
            progress_callback,
            "generation",
            "complete"
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
        start = time.perf_counter()

        self._emit(
            progress_callback,
            "validation",
            "processing"
        )

        try:
            validation_results = run_all_validations(
                case_data,
                generated_text,
                generated_paragraphs
            )

            deterministic_score = calculate_deterministic_score(
                validation_results
            )
        except Exception:
            self._emit(
                progress_callback,
                "validation",
                "error",
                message=(
                    "The validation stage failed during generation."
                )
            )
            raise

        elapsed = time.perf_counter() - start
        print(f"[Timing] Validation: {elapsed:.2f}s")

        self._emit(
            progress_callback,
            "validation",
            "complete"
        )

        # 7. Run LLM evaluation
        start = time.perf_counter()
        self._emit(
            progress_callback,
            "evaluation",
            "processing"
        )

        try:
            evaluation_raw = self.evaluation_agent.run(
                case_data=case_data,
                reference_text=reference_text,
                generated_text=generated_text
            )

            evaluation_report = EvaluationReport.model_validate_json(
                evaluation_raw
            )
        except Exception:
            self._emit(
                progress_callback,
                "evaluation",
                "error",
                message=(
                    "The evaluation stage failed during generation."
                )
            )
            raise

        elapsed = time.perf_counter() - start
        print(f"[Timing] Evaluation: {elapsed:.2f}s")

        self._emit(
            progress_callback,
            "evaluation",
            "complete"
        )

        total_elapsed = time.perf_counter() - total_start
        print(f"[Timing] Total pipeline: {total_elapsed:.2f}s")

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