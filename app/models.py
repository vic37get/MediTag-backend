from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Enum
from datetime import datetime
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
import pytz
import enum
TMZ = pytz.timezone('America/Fortaleza')

class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(TMZ)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(TMZ),
        onupdate=lambda: datetime.now(TMZ)
    )

class StatusEnum(enum.Enum):
    PENDING = 'Pending'
    VALIDATED = 'Validated'
    IN_PROGRESS = 'In Progress'

class RoleEnum(enum.Enum):
    ADMIN = 'admin'
    MEDICO = 'medico'
    TECNICO = 'tecnico'

class Estudo(Base):
    __tablename__ = "estudo"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    workspace: Mapped[str] = mapped_column(String, nullable=False)
    task: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[str] = mapped_column(String, nullable=False)
    description = Column(Text, nullable=True)

    labels: Mapped[list['Label']] = relationship(
        back_populates='estudo',
        cascade='all, delete-orphan',
        uselist=True
    )

class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

class Label(Base):
    __tablename__ = "label"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_estudo: Mapped[int] = mapped_column(Integer, ForeignKey('estudo.id'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=False)
    multi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    estudo: Mapped['Estudo'] = relationship(
        back_populates='labels'
    )

class Amostra(Base):
    __tablename__ = "amostra"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_estudo: Mapped[int] = mapped_column(Integer, ForeignKey('estudo.id'))
    image_path: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    report: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum, name='status_enum'), nullable=False, default=StatusEnum.PENDING)

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, name='role_enum'), nullable=False)

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))