"""
Patient Agent for handling patient communication, FAQ, consent, and notifications
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.patient import Patient, AnxietyLevel
from src.models.faq import FAQ
from src.models.notification import Notification, NotificationType, NotificationCategory, NotificationStatus
from src.models.consent import Consent, ConsentType, ConsentStatus
from src.config import settings


class PatientAgent:
    """Patient Agent for managing patient interactions."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_base_url = settings.LLM_BASE_URL
        self.llm_api_key = settings.LLM_API_KEY
        self.llm_model = settings.LLM_MODEL

    async def answer_faq(self, question: str, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Answer patient FAQ using semantic search and LLM.
        """
        # Search for relevant FAQs
        result = await self.db.execute(
            select(FAQ).where(FAQ.is_active == True)
        )
        faqs = result.scalars().all()

        # Simple keyword matching (in production, use embeddings)
        relevant_faqs = []
        question_lower = question.lower()

        for faq in faqs:
            # Check keywords
            if faq.keywords:
                keywords = [k.strip().lower() for k in faq.keywords.split(",")]
                if any(k in question_lower for k in keywords):
                    relevant_faqs.append(faq)
                    continue

            # Check if question words appear in the FAQ question
            question_words = set(question_lower.split())
            faq_words = set(faq.question.lower().split())
            if question_words & faq_words:
                relevant_faqs.append(faq)

        # If we found relevant FAQs, use the most relevant one
        if relevant_faqs:
            best_faq = relevant_faqs[0]

            # Increment view count
            best_faq.view_count += 1
            await self.db.commit()

            return {
                "answer": best_faq.answer,
                "category": best_faq.category,
                "faq_id": best_faq.id,
                "confidence": "high" if len(relevant_faqs) == 1 else "medium",
            }

        # Use LLM to generate answer if no FAQ found
        answer = await self._generate_faq_answer(question)

        return {
            "answer": answer,
            "category": "general",
            "faq_id": None,
            "confidence": "low",
        }

    async def _generate_faq_answer(self, question: str) -> str:
        """Generate FAQ answer using LLM."""
        # This is a placeholder - in production, call the LLM
        return (
            "I understand you have a question about your CT brain scan. "
            "Please contact our staff or speak with your healthcare provider "
            "for more specific information about your procedure."
        )

    async def assess_anxiety(self, patient_id: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess patient anxiety level based on questionnaire responses.
        """
        result = await self.db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()

        if not patient:
            raise ValueError("Patient not found")

        # Simple anxiety scoring based on responses
        # In production, use a validated anxiety scale
        score = 0

        # Questions about anxiety symptoms
        if responses.get("nervous"):
            score += int(responses["nervous"])
        if responses.get("worrying"):
            score += int(responses.get("worrying", 0))
        if responses.get("relaxation_difficulty"):
            score += int(responses["relaxation_difficulty"])
        if responses.get("previous_ct_experience"):
            if responses["previous_ct_experience"] == "negative":
                score += 2

        # Determine anxiety level
        if score <= 2:
            anxiety_level = AnxietyLevel.NONE
        elif score <= 5:
            anxiety_level = AnxietyLevel.MILD
        elif score <= 8:
            anxiety_level = AnxietyLevel.MODERATE
        else:
            anxiety_level = AnxietyLevel.SEVERE

        # Update patient record
        patient.anxiety_level = anxiety_level
        await self.db.commit()

        # Generate recommendations based on anxiety level
        recommendations = self._get_anxiety_recommendations(anxiety_level)

        return {
            "patient_id": patient_id,
            "anxiety_level": anxiety_level.value,
            "score": score,
            "recommendations": recommendations,
        }

    def _get_anxiety_recommendations(self, anxiety_level: AnxietyLevel) -> List[str]:
        """Get recommendations based on anxiety level."""
        recommendations = {
            AnxietyLevel.NONE: [
                "Your CT scan is routine. Our staff will guide you through the process.",
            ],
            AnxietyLevel.MILD: [
                "Consider listening to calming music during the scan.",
                "Let our staff know if you'd like any additional support.",
            ],
            AnxietyLevel.MODERATE: [
                "We recommend our VR relaxation program before the scan.",
                "A staff member will stay with you throughout the procedure.",
                "Deep breathing exercises can help you relax.",
            ],
            AnxietyLevel.SEVERE: [
                "Please speak with our care team about your concerns.",
                "We can arrange a pre-visit to familiarize you with the equipment.",
                "VR relaxation is strongly recommended before your scan.",
                "Sedation options may be available - please discuss with your doctor.",
            ],
        }

        return recommendations.get(anxiety_level, [])

    async def send_notification(
        self,
        patient_id: str,
        notification_type: NotificationType,
        category: NotificationCategory,
        title: str,
        message: str,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send notification to patient."""
        # Get patient for contact info
        result = await self.db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()

        if not patient:
            raise ValueError("Patient not found")

        # Create notification record
        notification = Notification(
            patient_id=patient_id,
            notification_type=notification_type,
            category=category,
            title=title,
            message=message,
            recipient_phone=patient.phone,
            recipient_email=patient.email,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )

        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        # In production, integrate with SMS/WhatsApp/Email providers
        # For now, mark as pending and simulate sending
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        await self.db.commit()

        return {
            "notification_id": notification.id,
            "status": notification.status.value,
            "sent_at": notification.sent_at.isoformat(),
        }

    async def get_vr_content(self, anxiety_level: AnxietyLevel) -> List[Dict[str, Any]]:
        """Get VR relaxation content recommendations."""
        # VR content library (in production, store in database)
        vr_content = [
            {
                "id": "vr-1",
                "title": "Peaceful Forest",
                "description": "A serene forest setting with gentle breeze and ambient sounds",
                "duration_minutes": 10,
                "category": "nature",
                "suitable_for": ["none", "mild", "moderate"],
            },
            {
                "id": "vr-2",
                "title": "Ocean Waves",
                "description": "Relaxing beach scene with rhythmic waves",
                "duration_minutes": 15,
                "category": "nature",
                "suitable_for": ["none", "mild", "moderate", "severe"],
            },
            {
                "id": "vr-3",
                "title": "Guided Meditation",
                "description": "Voice-guided breathing and relaxation exercises",
                "duration_minutes": 8,
                "category": "meditation",
                "suitable_for": ["mild", "moderate", "severe"],
            },
            {
                "id": "vr-4",
                "title": "Underwater World",
                "description": "Calming underwater exploration with fish and gentle currents",
                "duration_minutes": 12,
                "category": "nature",
                "suitable_for": ["none", "mild", "moderate"],
            },
            {
                "id": "vr-5",
                "title": "Mountain Sunrise",
                "description": "Witness a beautiful sunrise from a peaceful mountain top",
                "duration_minutes": 10,
                "category": "nature",
                "suitable_for": ["none", "mild", "moderate"],
            },
        ]

        # Filter by anxiety level
        anxiety_str = anxiety_level.value
        suitable_content = [
            c for c in vr_content
            if anxiety_str in c["suitable_for"]
        ]

        return suitable_content

    async def process_digital_consent(
        self,
        patient_id: str,
        consent_type: ConsentType,
        consent_given: bool,
        signature_data: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process digital consent."""
        result = await self.db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()

        if not patient:
            raise ValueError("Patient not found")

        # Create consent record
        consent = Consent(
            patient_id=patient_id,
            consent_type=consent_type,
            status=ConsentStatus.SIGNED if consent_given else ConsentStatus.DECLINED,
            consent_text=self._get_consent_text(consent_type),
            signature_data=signature_data,
            signed_at=datetime.utcnow() if consent_given else None,
        )

        self.db.add(consent)

        # Update patient consent status
        if consent_given and consent_type == ConsentType.CT_SCAN:
            patient.consent_given = True
            patient.consent_timestamp = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(consent)

        return {
            "consent_id": consent.id,
            "status": consent.status.value,
            "signed_at": consent.signed_at.isoformat() if consent.signed_at else None,
        }

    def _get_consent_text(self, consent_type: ConsentType) -> str:
        """Get consent form text based on type."""
        consent_texts = {
            ConsentType.CT_SCAN: """
CT BRAIN SCAN CONSENT FORM

Procedure: CT Brain Scan
Purpose: To obtain detailed images of your brain

I understand that:
1. A CT scan uses X-rays to create cross-sectional images of the brain
2. The procedure is painless and typically takes 15-30 minutes
3. I will need to lie still on a scanning table
4. Contrast dye may be used to enhance images (separate consent required)

Risks:
- Small amount of radiation exposure
- Rare allergic reaction to contrast dye
- Possible discomfort from lying still

I have had the opportunity to ask questions and have them answered to my satisfaction.
            """,
            ConsentType.CONTRAST: """
CONTRAST AGENT CONSENT FORM

I consent to the administration of contrast dye for my CT scan.

I understand that:
1. Contrast dye helps highlight blood vessels and tissues
2. It will be injected through an IV
3. I may feel a warm sensation or metallic taste
4. Rarely, allergic reactions can occur

I have informed the staff of any previous reactions to contrast agents.
            """,
        }

        return consent_texts.get(consent_type, "Consent form text not available.")