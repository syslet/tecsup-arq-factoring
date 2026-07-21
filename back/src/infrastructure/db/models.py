from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.session import Base


class UserModel(Base):
    """SQLAlchemy model for the users table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dni: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="GIRADOR")
    verification_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING_VERIFICATION"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    sessions: Mapped[list["SessionModel"]] = relationship(
        "SessionModel", back_populates="user", cascade="all, delete-orphan"
    )
    company: Mapped["CompanyModel | None"] = relationship(
        "CompanyModel", back_populates="legal_representative", uselist=False
    )


class CompanyModel(Base):
    """SQLAlchemy model for companies table (Entidad Jurídica)."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ruc: Mapped[str] = mapped_column(String(11), unique=True, nullable=False, index=True)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_representative_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bank_account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    cci: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="PEN")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    legal_representative: Mapped["UserModel"] = relationship("UserModel", back_populates="company")
    documents: Mapped[list["CompanyDocumentModel"]] = relationship(
        "CompanyDocumentModel", back_populates="company", cascade="all, delete-orphan"
    )


class CompanyDocumentModel(Base):
    """SQLAlchemy model for company_documents table."""

    __tablename__ = "company_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    company: Mapped["CompanyModel"] = relationship("CompanyModel", back_populates="documents")


class SessionModel(Base):
    """SQLAlchemy model for user_sessions table."""

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_jti: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="sessions")


class InvoiceSheetModel(Base):
    """SQLAlchemy model for invoice_sheets table."""

    __tablename__ = "invoice_sheets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sheet_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="PEN")
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    advance_amount: Mapped[float] = mapped_column(Float, nullable=False)
    interest_fee: Mapped[float] = mapped_column(Float, nullable=False)
    commission: Mapped[float] = mapped_column(Float, nullable=False)
    net_disbursement: Mapped[float] = mapped_column(Float, nullable=False)
    advance_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.85)
    monthly_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.02)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="QUOTED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    invoices: Mapped[list["InvoiceModel"]] = relationship(
        "InvoiceModel", back_populates="sheet", cascade="all, delete-orphan"
    )
    negotiations: Mapped[list["NegotiationHistoryModel"]] = relationship(
        "NegotiationHistoryModel", back_populates="sheet", cascade="all, delete-orphan"
    )


class InvoiceModel(Base):
    """SQLAlchemy model for invoices table."""

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sheet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("invoice_sheets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False)
    drawer_ruc: Mapped[str] = mapped_column(String(11), nullable=False)
    debtor_ruc: Mapped[str] = mapped_column(String(11), nullable=False)
    debtor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_to_maturity: Mapped[int] = mapped_column(Integer, nullable=False)
    sunat_status: Mapped[str] = mapped_column(String(20), nullable=False, default="VALID")
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    sheet: Mapped["InvoiceSheetModel"] = relationship(
        "InvoiceSheetModel", back_populates="invoices"
    )


class DisbursementModel(Base):
    """SQLAlchemy model for disbursements table."""

    __tablename__ = "disbursements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sheet_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("invoice_sheets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    annotation_code: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="PEN")
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bank_account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    cci: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DISBURSED")
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    sheet: Mapped["InvoiceSheetModel"] = relationship("InvoiceSheetModel")


class NegotiationHistoryModel(Base):
    """SQLAlchemy model for negotiation_histories table."""

    __tablename__ = "negotiation_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sheet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("invoice_sheets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requested_rate: Mapped[float] = mapped_column(Float, nullable=False)
    offered_rate: Mapped[float] = mapped_column(Float, nullable=False)
    requested_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    sheet: Mapped["InvoiceSheetModel"] = relationship(
        "InvoiceSheetModel", back_populates="negotiations"
    )

