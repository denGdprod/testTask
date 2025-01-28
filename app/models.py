from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):

    id: so.Mapped[int] = so.mapped_column(primary_key=True, unique=True, autoincrement=True)
    login: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[str | None] = so.mapped_column(sa.String(256))
    user_type:  so.Mapped[str] = so.mapped_column(sa.String(120), default='user')
    telegram_id: so.Mapped[int] = so.mapped_column(sa.Integer, index=True, unique=True, nullable=False)

    partner: so.Mapped['Partner'] = so.relationship(back_populates='user', uselist=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.login}>'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Partner(db.Model):

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    user: so.Mapped[User] = so.relationship(back_populates='partner')
    servers: so.Mapped['Server'] = so.relationship(back_populates="partner")

    __mapper_args__ = {
        'polymorphic_identity': 'partner'
    }

    def __repr__(self):
        return f'<Partner user_id={self.user_id}>'


class Server(db.Model):

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False, index=True)
    price: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False, default=0.0)
    url: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    panel_login: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    panel_password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    partner_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Partner.id), index=True, nullable=False)

    partner: so.Mapped[Partner] = so.relationship(back_populates="servers")
    keys: so.Mapped['Key'] = so.relationship(back_populates='server')

    def set_password(self, password):
        self.panel_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.panel_password_hash, password)

    def __repr__(self):
        return f'<Server {self.name} partner id {self. partner_id}>'


class Key(db.Model):

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    created: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    code: so.Mapped[str] = so.mapped_column(sa.String, unique=True, nullable=False)
    bonus: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False, default=0.0)
    payed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, nullable=False)
    payed_date: so.Mapped[Optional[datetime]] = so.mapped_column(index=True,
                                                                 default=lambda: datetime.now(timezone.utc))
    server_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Server.id), index=True, nullable=False)

    server: so.Mapped[Server] = so.relationship(back_populates="keys")

    def __repr__(self):
        return f"key {self.code} server id {self.server_id}"
