"""
Script to create sample PDF and TXT documents for testing and live demonstration.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents")
os.makedirs(DOCS_DIR, exist_ok=True)

def create_sample_pdf(filename, title, content_paragraphs):
    path = os.path.join(DOCS_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0f223d"),
        spaceAfter=15
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=10
    )
    
    story = [Paragraph(title, title_style), Spacer(1, 10)]
    for p in content_paragraphs:
        story.append(Paragraph(p, body_style))
        
    doc.build(story)
    print(f"Generated sample PDF: {path}")

def create_sample_txt(filename, content):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated sample TXT: {path}")

def generate_all_samples():
    # 1. Sample NDA PDF
    create_sample_pdf(
        "sample_nda.pdf",
        "MUTUAL NON-DISCLOSURE AND PROPRIETARY INFORMATION AGREEMENT",
        [
            "This Agreement is entered into by and between TechInnovate Corp ('Disclosing Party') and SecureData Systems ('Receiving Party').",
            "1. CONFIDENTIAL INFORMATION. The Receiving Party agrees to treat all technical data, proprietary source code, software architecture designs, algorithmic models, and business trade secrets as strictly confidential.",
            "2. OBLIGATIONS. The Receiving Party shall hold and maintain the Proprietary Information in strictest confidence and shall not disclose such information to any third party without prior written consent of the Disclosing Party.",
            "3. RETURN OF MATERIALS. Upon termination of discussions, the Receiving Party shall promptly return or certify destruction of all tangible confidential documents, electronic media, and backups.",
            "4. GOVERNING LAW. This Agreement shall be construed and governed in accordance with the laws of the State of New York."
        ]
    )

    # 2. Sample Lease PDF
    create_sample_pdf(
        "sample_lease.pdf",
        "STANDARD RESIDENTIAL APARTMENT LEASE AGREEMENT",
        [
            "This Lease Agreement is made between Landlord (Apex Properties LLC) and Tenant (Alexander Wright) for residential premises located at Unit 4B, 108 Park Avenue.",
            "1. TERM AND RENT. The lease term begins on November 1, 2026. The monthly rent shall be $2,450 payable on the first day of each month.",
            "2. SECURITY DEPOSIT. Tenant agrees to deposit $4,900 as security deposit against property damage, unpaid rent, and tenant breach.",
            "3. MAINTENANCE AND REPAIRS. Tenant covenants to maintain the demised premises in a clean and tenantable condition. Landlord shall be responsible for structural maintenance and heating systems.",
            "4. DEFAULT AND EVICTION. In the event of rent delinquency exceeding 14 calendar days, Landlord may issue notice to vacate or initiate eviction proceedings."
        ]
    )

    # 3. Sample Employment Contract TXT
    emp_content = """EXECUTIVE EMPLOYMENT AGREEMENT

This Employment Agreement is entered into between CloudScale Technologies Inc. ("Employer") and Jordan Miller ("Employee").

1. POSITION AND DUTIES
Employee shall serve in the executive role of Senior Director of Engineering, reporting directly to the Vice President of Product Engineering.

2. COMPENSATION AND BENEFITS
Employer agrees to pay an annual base salary of $175,000, payable in bi-weekly disbursements subject to statutory tax withholding. Employee is eligible for the annual performance bonus, comprehensive health insurance, and 401(k) retirement matching.

3. RESTRICTIVE COVENANTS AND NON-COMPETE
During the term of employment and for twelve (12) months following termination, Employee covenants not to solicit customers or employees of Employer or engage in competing software engineering enterprises within North America.

4. TERMINATION
Employment is at-will. Either party may terminate this agreement upon thirty (30) days advance written notice.
"""
    create_sample_txt("sample_employment.txt", emp_content)

    # 4. Sample Court Judgment TXT
    judg_content = """IN THE HIGH COURT OF COMMERCIAL JUDICATURE
Case No: COMM-APP-2025-0849

Between:
Meridian Global Logistics Ltd. (Claimant / Appellant)
and
Continental Cargo Carriers Inc. (Defendant / Respondent)

JUDGMENT AND ORDER
Before the Honorable Justice H. Thornton

The Claimant brings this appeal seeking recovery of damages and cargo compensation resulting from maritime breach of carriage under the bill of lading.

Having considered the submissions of learned counsel and reviewed the admiralty documentation and surveyor reports, this Court holds that the exemption clause relied upon by the Defendant does not relieve the carrier from ordinary duty of seaworthy care.

ORDER:
1. The appeal is ALLOWED.
2. The Defendant is ordered to pay the sum of $320,000 in liquidated damages together with interest at 6% per annum.
3. Costs awarded to Claimant.
"""
    create_sample_txt("sample_court_judgment.txt", judg_content)

if __name__ == "__main__":
    generate_all_samples()
