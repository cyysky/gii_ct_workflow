"""
Clinical Agent for triage decision support, urgency scoring, and CT indication validation
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.ct_scan import CTScan, UrgencyLevel, AppropriatenessScore
from src.models.patient import Patient


class ClinicalAgent:
    """Clinical Agent for medical decision support."""

    # Clinical guidelines (simplified for demo)
    HIGH_URGENCY_INDICATIONS = [
        "acute stroke",
        "suspected hemorrhage",
        "head trauma",
        "altered consciousness",
        "seizure",
        "focal neurological deficit",
        "suspected tumor with mass effect",
    ]

    URGENT_INDICATIONS = [
        "headache with neurological symptoms",
        "dizziness with risk factors",
        "post-operative evaluation",
        "suspected infection",
        "hydrocephalus",
    ]

    # UCLA CT Appropriateness Criteria (simplified)
    APPROPRIATENESS_CRITERIA = {
        "head trauma, mild with loss of consciousness": 8,
        "head trauma, mild without loss of consciousness": 4,
        "head trauma, moderate to severe": 9,
        "acute stroke symptoms": 9,
        "altered mental status": 7,
        "headache with focal neurological findings": 8,
        "headache without focal findings": 2,
        "seizure with focal features": 8,
        "seizure without focal features": 3,
        "suspected brain tumor": 7,
        "dizziness/vertigo": 3,
        "syncope": 4,
        "cognitive decline": 6,
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_ct_indication(
        self,
        ct_indication: str,
        clinical_history: Optional[str] = None,
        symptoms: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze CT indication and provide clinical decision support.
        """
        # Normalize text
        indication_lower = ct_indication.lower()
        history_lower = clinical_history.lower() if clinical_history else ""
        symptoms_lower = symptoms.lower() if symptoms else ""

        combined_text = f"{indication_lower} {history_lower} {symptoms_lower}"

        # Determine urgency level
        urgency_level = self._determine_urgency(combined_text)

        # Calculate appropriateness score
        appropriateness_score, appropriateness_reason = self._calculate_appropriateness(
            combined_text
        )

        # Generate clinical recommendations
        recommendations = self._generate_recommendations(
            urgency_level, appropriateness_score, combined_text
        )

        return {
            "urgency_level": urgency_level.value,
            "urgency_reason": self._get_urgency_reason(urgency_level),
            "appropriateness_score": appropriateness_score.value,
            "appropriateness_reason": appropriateness_reason,
            "recommendations": recommendations,
            "requires_radiologist_review": urgency_level == UrgencyLevel.IMMEDIATE,
        }

    def _determine_urgency(self, text: str) -> UrgencyLevel:
        """Determine urgency level based on clinical indicators."""
        # Check for immediate urgency indicators
        immediate_indicators = [
            "stroke",
            "hemorrhage",
            "bleeding",
            "seizure",
            "unconscious",
            "coma",
            "focal deficit",
            "mass effect",
            "herniation",
        ]

        if any(indicator in text for indicator in immediate_indicators):
            return UrgencyLevel.IMMEDIATE

        # Check for urgent indicators
        urgent_indicators = [
            "trauma",
            "head injury",
            "confusion",
            "altered",
            "persistent headache",
            "vomiting",
            "papilledema",
        ]

        if any(indicator in text for indicator in urgent_indicators):
            return UrgencyLevel.URGENT

        # Default to routine
        return UrgencyLevel.ROUTINE

    def _calculate_appropriateness(
        self, text: str
    ) -> tuple[AppropriatenessScore, str]:
        """Calculate UCLA CT Appropriateness score."""
        # Match against criteria
        best_match_score = 0
        best_match_reason = "No specific criteria matched"

        for criteria, score in self.APPROPRIATENESS_CRITERIA.items():
            # Simple keyword matching
            criteria_words = set(criteria.split())
            text_words = set(text.split())

            overlap = criteria_words & text_words

            if len(overlap) >= min(2, len(criteria_words)):
                if score > best_match_score:
                    best_match_score = score
                    best_match_reason = f"Matched criteria: {criteria}"

        # Determine score category
        if best_match_score >= 7:
            appropriateness = AppropriatenessScore.VERY_HIGH
        elif best_match_score >= 6:
            appropriateness = AppropriatenessScore.HIGH
        elif best_match_score >= 4:
            appropriateness = AppropriatenessScore.MODERATE
        elif best_match_score >= 2:
            appropriateness = AppropriatenessScore.LOW
        else:
            appropriateness = AppropriatenessScore.VERY_LOW

        return appropriateness, f"Score: {best_match_score}/9 - {best_match_reason}"

    def _get_urgency_reason(self, urgency_level: UrgencyLevel) -> str:
        """Get human-readable reason for urgency level."""
        reasons = {
            UrgencyLevel.IMMEDIATE: (
                "Clinical findings suggest potentially life-threatening condition "
                "requiring immediate imaging."
            ),
            UrgencyLevel.URGENT: (
                "Clinical findings suggest condition requiring imaging within 1 hour."
            ),
            UrgencyLevel.ROUTINE: (
                "Clinical findings suggest routine imaging is appropriate. "
                "Scan can be scheduled within 24 hours."
            ),
        }
        return reasons.get(urgency_level, "")

    def _generate_recommendations(
        self,
        urgency_level: UrgencyLevel,
        appropriateness: AppropriatenessScore,
        text: str,
    ) -> List[str]:
        """Generate clinical recommendations."""
        recommendations = []

        # Urgency-based recommendations
        if urgency_level == UrgencyLevel.IMMEDIATE:
            recommendations.extend([
                "Order scan as STAT - immediate priority",
                "Notify radiology immediately",
                "Consider pre-notification for potential thrombolysis",
                "Ensure IV access for potential contrast",
            ])
        elif urgency_level == UrgencyLevel.URGENT:
            recommendations.extend([
                "Order scan as urgent - within 1 hour",
                "Notify radiology of urgent priority",
                "Prepare patient for scan",
            ])
        else:
            recommendations.extend([
                "Order scan as routine",
                "Schedule based on scanner availability",
            ])

        # Appropriateness-based recommendations
        if appropriateness in [AppropriatenessScore.LOW, AppropriatenessScore.VERY_LOW]:
            recommendations.extend([
                "Consider clinical consultation before proceeding",
                "CT may have limited diagnostic value for this indication",
                "Alternative imaging (MRI) may be more appropriate",
            ])

        # Specific clinical recommendations
        if "stroke" in text:
            recommendations.extend([
                "NIH Stroke Scale assessment required",
                "Determine last known well time",
                "Check eligibility for thrombolysis",
            ])

        if "trauma" in text:
            recommendations.extend([
                "Assess for other injuries",
                "Consider C-spine clearance",
                "Monitor Glasgow Coma Scale",
            ])

        if "seizure" in text:
            recommendations.extend([
                "Check anticonvulsant levels if applicable",
                "Consider EEG if indicated",
                "Assess for status epilepticus",
            ])

        return recommendations

    async def update_scan_with_analysis(
        self,
        scan_id: str,
        analysis_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update CT scan with clinical analysis results."""
        result = await self.db.execute(select(CTScan).where(CTScan.id == scan_id))
        scan = result.scalar_one_or_none()

        if not scan:
            raise ValueError("CT scan not found")

        # Update scan with analysis
        scan.urgency_level = UrgencyLevel(analysis_result["urgency_level"])
        scan.appropriateness_score = AppropriatenessScore(
            analysis_result["appropriateness_score"]
        )
        scan.appropriateness_reason = analysis_result["appropriateness_reason"]

        # Validate scan (move from ordered to validated)
        if scan.status.value == "ordered":
            scan.status = "validated"  # Use string for enum

        await self.db.commit()
        await db.refresh(scan)

        return {
            "scan_id": scan.id,
            "urgency_level": scan.urgency_level.value,
            "appropriateness_score": scan.appropriateness_score.value,
            "status": scan.status.value,
        }

    async def calculate_gcs_score(
        self,
        eye_response: int,
        verbal_response: int,
        motor_response: int,
    ) -> Dict[str, Any]:
        """
        Calculate Glasgow Coma Scale score.
        """
        total_score = eye_response + verbal_response + motor_response

        # Determine severity
        if total_score >= 13:
            severity = "mild"
        elif total_score >= 9:
            severity = "moderate"
        else:
            severity = "severe"

        return {
            "total_score": total_score,
            "eye": eye_response,
            "verbal": verbal_response,
            "motor": motor_response,
            "severity": severity,
            "interpretation": self._interpret_gcs(total_score),
        }

    def _interpret_gcs(self, score: int) -> str:
        """Interpret GCS score."""
        interpretations = {
            15: "Normal consciousness",
            13: "Minor brain injury",
            9: "Moderate brain injury",
            8: "Severe brain injury (coma)",
        }

        # Find closest interpretation
        for key in sorted(interpretations.keys(), reverse=True):
            if score >= key:
                return interpretations[key]

        return "Critical - immediate intervention required"

    async def suggest_additional_clinical_info(
        self,
        ct_indication: str,
    ) -> List[str]:
        """
        Suggest additional clinical information needed for better decision support.
        """
        suggestions = []
        indication_lower = ct_indication.lower()

        # Basic suggestions for all cases
        suggestions.append("Time of symptom onset or last known well")

        if "stroke" in indication_lower:
            suggestions.extend([
                "NIH Stroke Scale score",
                "Current anticoagulation status",
                "Recent surgery or bleeding history",
            ])

        if "trauma" in indication_lower:
            suggestions.extend([
                "Mechanism of injury",
                "Loss of consciousness duration",
                "Glasgow Coma Scale score",
                "Signs of focal neurological deficit",
            ])

        if "headache" in indication_lower:
            suggestions.extend([
                "Headache characteristics (thunderclap, progressive)",
                "Associated symptoms (vomiting, visual changes)",
                "History of similar headaches",
            ])

        if "seizure" in indication_lower:
            suggestions.extend([
                "Type of seizure",
                "Post-ictal period duration",
                "Anticonvulsant medications",
            ])

        return suggestions


# Fix import issue
from sqlalchemy import desc
from src.models.ct_scan import ScanStatus