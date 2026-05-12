"""
Resume and Job Description parsing service.
Handles PDF, DOCX, and TXT formats.
Extracts structured sections using rule-based NLP.
"""
import io
import re
from dataclasses import dataclass, field
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)

# Section header patterns (case-insensitive)
SECTION_PATTERNS = {
    "summary": r"(summary|objective|profile|about)",
    "experience": r"(experience|work history|employment|career)",
    "education": r"(education|academic|degree|qualification)",
    "skills": r"(skills|technical skills|competencies|technologies)",
    "projects": r"(projects|portfolio|work samples)",
    "certifications": r"(certifications?|licenses?|credentials?|awards?)",
    "publications": r"(publications?|research|papers?)",
}


@dataclass
class ParsedResume:
    raw_text: str
    sections: dict[str, str] = field(default_factory=dict)
    contact_info: dict[str, str] = field(default_factory=dict)
    skills_section: str = ""
    experience_section: str = ""
    education_section: str = ""

    def to_dict(self) -> dict:
        return {
            "sections": self.sections,
            "contact_info": self.contact_info,
            "skills_section": self.skills_section,
            "experience_section": self.experience_section,
            "education_section": self.education_section,
        }


@dataclass
class ParsedJobDescription:
    raw_text: str
    title: str = ""
    company: str = ""
    requirements_section: str = ""
    responsibilities_section: str = ""
    qualifications_section: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "company": self.company,
            "requirements_section": self.requirements_section,
            "responsibilities_section": self.responsibilities_section,
        }


class DocumentParser:
    """Extracts plain text from PDF, DOCX, and TXT files."""

    def parse_bytes(self, content: bytes, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext == "pdf":
            return self._parse_pdf(content)
        elif ext == "docx":
            return self._parse_docx(content)
        else:
            return content.decode("utf-8", errors="replace")

    def _parse_pdf(self, content: bytes) -> str:
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages)
        except ImportError:
            logger.warning("pdfplumber not installed, trying pypdf")
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(content))
                return "\n".join(p.extract_text() or "" for p in reader.pages)
            except Exception as e:
                logger.error("PDF parsing failed", error=str(e))
                return ""

    def _parse_docx(self, content: bytes) -> str:
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join(para.text for para in doc.paragraphs)
        except Exception as e:
            logger.error("DOCX parsing failed", error=str(e))
            return ""


class ResumeParser:
    """Parses raw resume text into structured sections."""

    def parse(self, raw_text: str) -> ParsedResume:
        cleaned = self._clean_text(raw_text)
        sections = self._extract_sections(cleaned)
        contact = self._extract_contact(cleaned)

        return ParsedResume(
            raw_text=raw_text,
            sections=sections,
            contact_info=contact,
            skills_section=sections.get("skills", ""),
            experience_section=sections.get("experience", ""),
            education_section=sections.get("education", ""),
        )

    def _clean_text(self, text: str) -> str:
        # Normalize whitespace
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _extract_sections(self, text: str) -> dict[str, str]:
        """Split text by detected section headers."""
        lines = text.split("\n")
        sections: dict[str, str] = {}
        current_section = "header"
        buffer: list[str] = []

        for line in lines:
            stripped = line.strip()
            matched_section = self._match_section_header(stripped)
            if matched_section:
                if buffer:
                    sections[current_section] = "\n".join(buffer).strip()
                current_section = matched_section
                buffer = []
            else:
                buffer.append(line)

        if buffer:
            sections[current_section] = "\n".join(buffer).strip()

        return sections

    def _match_section_header(self, line: str) -> Optional[str]:
        """Return section key if line is a section header."""
        if len(line) > 60 or len(line) < 2:
            return None
        for section_key, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                return section_key
        return None

    def _extract_contact(self, text: str) -> dict[str, str]:
        contact: dict[str, str] = {}

        # Email
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
        if email_match:
            contact["email"] = email_match.group()

        # Phone
        phone_match = re.search(
            r"(\+?\d[\d\s\-().]{7,}\d)", text
        )
        if phone_match:
            contact["phone"] = phone_match.group().strip()

        # LinkedIn
        linkedin_match = re.search(r"linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group()

        # GitHub
        github_match = re.search(r"github\.com/[\w-]+", text, re.IGNORECASE)
        if github_match:
            contact["github"] = github_match.group()

        return contact


class JobDescriptionParser:
    """Parses job descriptions into structured form."""

    JD_SECTION_PATTERNS = {
        "requirements": r"(requirements?|required|must have|qualifications?)",
        "responsibilities": r"(responsibilities|duties|what you.ll do|role)",
        "nice_to_have": r"(nice to have|preferred|bonus|plus)",
        "about": r"(about us|about the (company|role|team))",
    }

    def parse(self, raw_text: str) -> ParsedJobDescription:
        cleaned = raw_text.strip()
        title = self._extract_title(cleaned)
        company = self._extract_company(cleaned)
        sections = self._extract_jd_sections(cleaned)

        return ParsedJobDescription(
            raw_text=raw_text,
            title=title,
            company=company,
            requirements_section=sections.get("requirements", ""),
            responsibilities_section=sections.get("responsibilities", ""),
            qualifications_section=sections.get("nice_to_have", ""),
        )

    def _extract_title(self, text: str) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return lines[0] if lines else "Unknown Role"

    def _extract_company(self, text: str) -> str:
        patterns = [
            r"at\s+([A-Z][a-zA-Z0-9\s&,.]+?)(?:\.|,|\n)",
            r"([A-Z][a-zA-Z0-9\s&,.]+?)\s+is (?:looking|hiring|seeking)",
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1).strip()
        return ""

    def _extract_jd_sections(self, text: str) -> dict[str, str]:
        lines = text.split("\n")
        sections: dict[str, str] = {}
        current = "intro"
        buffer: list[str] = []

        for line in lines:
            stripped = line.strip()
            matched = self._match_jd_section(stripped)
            if matched:
                if buffer:
                    sections[current] = "\n".join(buffer).strip()
                current = matched
                buffer = []
            else:
                buffer.append(line)

        if buffer:
            sections[current] = "\n".join(buffer).strip()

        return sections

    def _match_jd_section(self, line: str) -> Optional[str]:
        if len(line) > 80 or len(line) < 2:
            return None
        for key, pattern in self.JD_SECTION_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                return key
        return None
