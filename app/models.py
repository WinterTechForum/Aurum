from geoalchemy2 import Geometry
from sqlalchemy import Integer, Column, String, Text, Float, Date
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class MiningDistrict(Base):
    __tablename__ = 'mining_district'

    id = Column("gid", Integer, primary_key=True)
    district = Column(String(255), nullable=False)
    webpage = Column(Text, nullable=True)
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=26913))

    def __repr__(self):
        return f"<MiningDistrict(name={self.district})>"

class ActiveClaims(Base):
    __tablename__ = "active_claims"

    gid = Column(Integer, primary_key=True)
    serial_no = Column(String(9))
    dispositio = Column(String(6))
    casetyp_cd = Column(String(6))
    casetyp_tx = Column(String(14))
    case_acres = Column(String(7))
    commodity = Column(String(22))
    geo_name = Column(String(17))
    claim_nm = Column(String(23))
    locate_dt = Column(String(10))
    name_1 = Column(String(43))
    intrel_1 = Column(String(8))
    perint_1 = Column(String(5))
    name_2 = Column(String(40))
    intrel_2 = Column(String(8))
    perint_2 = Column(String(3))
    name_3 = Column(String(49))
    intrel_3 = Column(String(8))
    perint_3 = Column(String(3))
    name_4 = Column(String(29))
    intrel_4 = Column(String(8))
    perint_4 = Column(String(3))
    update_dt = Column(String(10))
    geom = Column(Geometry(geometry_type="MULTIPOLYGON", srid=26913))

    def __repr__(self):
        return f"<ActiveClaims(gid={self.gid}, serial_no={self.serial_no}, claim_nm={self.claim_nm}, commodity={self.commodity})>"

class InactiveClaims(Base):
    __tablename__ = "inactive_claims"

    gid = Column(Integer, primary_key=True)
    serial_no = Column(String(9))
    dispositio = Column(String(6))
    casetyp_cd = Column(String(6))
    casetyp_tx = Column(String(14))
    case_acres = Column(String(7))
    commodity = Column(String(23))
    geo_name = Column(String(19))
    claim_nm = Column(String(24))
    locate_dt = Column(String(10))
    name_1 = Column(String(43))
    intrel_1 = Column(String(8))
    perint_1 = Column(String(8))
    name_2 = Column(String(31))
    intrel_2 = Column(String(8))
    perint_2 = Column(String(8))
    name_3 = Column(String(29))
    intrel_3 = Column(String(8))
    perint_3 = Column(String(8))
    name_4 = Column(String(29))
    intrel_4 = Column(String(8))
    perint_4 = Column(String(8))
    update_dt = Column(String(10))
    geom = Column(Geometry(geometry_type="MULTIPOLYGON", srid=26913))

    def __repr__(self):
        return (
            f"<InactiveClaims(gid={self.gid}, serial_no={self.serial_no}, "
            f"claim_nm={self.claim_nm}, commodity={self.commodity})>"
        )

