from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Boolean,
    DateTime,
    Enum,
    Table
)
from datetime import datetime
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
import pytz
import enum
TMZ = pytz.timezone("America/Fortaleza")


class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(TMZ)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(TMZ),
        onupdate=lambda: datetime.now(TMZ),
    )


class StatusEnum(enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    IN_PROGRESS = "in progress"


class RoleEnum(enum.Enum):
    ADMIN = "admin"
    MEDICO = "medico"
    TECNICO = "tecnico"


label_amostra = Table(
    "label_amostra",
    Base.metadata,
    Column('id_amostra', ForeignKey('amostra.id'), primary_key=True),
    Column('id_label', ForeignKey('label.id'), primary_key=True)
)

estudo_tag = Table(
    "estudo_tag",
    Base.metadata,
    Column('id_estudo', ForeignKey('estudo.id'), primary_key=True),
    Column('id_tag', ForeignKey('tag.id'), primary_key=True)
)

estudo_user = Table(
    "estudo_user",
    Base.metadata,
    Column('id_estudo', ForeignKey('estudo.id'), primary_key=True),
    Column('id_user', ForeignKey('user.id'), primary_key=True)
)


class Estudo(Base):
    __tablename__ = "estudo"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey('workspace.id'))
    task: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[str] = mapped_column(String, nullable=False)
    description = Column(Text, nullable=True)

    labels: Mapped[list["Label"]] = relationship(
        back_populates="estudo",
        cascade="all, delete-orphan",
        uselist=True
    )

    tags: Mapped[list['Tag']] = relationship(
        secondary=estudo_tag,
        back_populates='estudos',
        uselist=True
    )

    amostras: Mapped[list['Amostra']] = relationship(
        back_populates="estudo",
        cascade="all, delete-orphan",
        uselist=True
    )

    users: Mapped[list['User']] = relationship(
        secondary=estudo_user,
        back_populates='estudos',
        uselist=True
    )

    workspace: Mapped['Workspace'] = relationship(
        back_populates='estudos'
    )


class Workspace(Base):
    __tablename__ = "workspace"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=False)

    estudos: Mapped[list['Estudo']] = relationship(
        back_populates='workspace',
        cascade="all, delete-orphan",
        uselist=True
    )


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    estudos: Mapped[list['Estudo']] = relationship(
        secondary=estudo_tag,
        back_populates='tags',
        uselist=True
    )


class Label(Base):
    __tablename__ = "label"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_estudo: Mapped[int] = mapped_column(Integer, ForeignKey("estudo.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=False)
    multi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    estudo: Mapped["Estudo"] = relationship(back_populates="labels")
    amostras: Mapped[list['Amostra']] = relationship(
        secondary=label_amostra,
        back_populates='labels',
        uselist=True
    )


class ImageAmostra(Base):
    __tablename__ = "image_amostra"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_path: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    id_amostra: Mapped[int] = mapped_column(Integer, ForeignKey("amostra.id"))

    amostra: Mapped['Amostra'] = relationship(
        back_populates='images'
    )


class Amostra(Base):
    __tablename__ = "amostra"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_estudo: Mapped[int] = mapped_column(Integer, ForeignKey("estudo.id"))
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)
    report: Mapped[str] = mapped_column(String, nullable=True)
    text_report: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="status_enum"), nullable=False, default=StatusEnum.PENDING
    )

    images: Mapped[list['ImageAmostra']] = relationship(
        back_populates='amostra',
        cascade="all, delete-orphan",
        uselist=True
    )

    labels: Mapped[list['Label']] = relationship(
        secondary=label_amostra,
        back_populates='amostras',
        uselist=True
    )

    estudo: Mapped['Estudo'] = relationship(
        back_populates='amostras'
    )

    user: Mapped['User'] = relationship(
        back_populates='amostras'
    )


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    estudos: Mapped[list['Estudo']] = relationship(
        secondary=estudo_user,
        back_populates='users',
        uselist=True
    )

    amostras: Mapped[list['Amostra']] = relationship(
        back_populates='user',
        uselist=True
    )


if __name__ == "__main__":
    from database import engine
    from models import Base

    def init_db():
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully!")

    init_db()