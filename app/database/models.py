from sqlalchemy import Column, Integer, String, JSON, ForeignKey

from sqlalchemy.orm import relationship

from app.database.base import Base


class CompanyDataORM(Base):
    __tablename__ = 'company_data'
    __table_args__ = {'schema': 'fastapi_schema'}

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    region = Column(String)
    industry = Column(String)

    bankruptcy_data = Column(JSON)

    region_info = relationship("CommonInfoRegion", back_populates="company")
    county_info = relationship("CommonInfoCounty", back_populates="company")
    industry_info = relationship("CommonInfoIndustry", back_populates="company")


class CommonInfoRegion(Base):
    __tablename__ = 'common_info_region'
    __table_args__ = {'schema': 'fastapi_schema'}

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, unique=True)
    total_companies = Column(Integer)
    profitable_companies = Column(Integer)
    debt_free_companies = Column(Integer)
    solvent_companies = Column(Integer)
    roa_companies = Column(Integer)

    company_id = Column(Integer, ForeignKey('fastapi_schema.company_data.id'))
    company = relationship("CompanyDataORM", back_populates="region_info")


class CommonInfoCounty(Base):
    __tablename__ = 'common_info_county'
    __table_args__ = {'schema': 'fastapi_schema'}

    id = Column(Integer, primary_key=True, index=True)
    county = Column(String, unique=True)
    total_companies = Column(Integer)
    profitable_companies = Column(Integer)
    debt_free_companies = Column(Integer)
    solvent_companies = Column(Integer)
    roa_companies = Column(Integer)

    company_id = Column(Integer, ForeignKey('fastapi_schema.company_data.id'))
    company = relationship("CompanyDataORM", back_populates="county_info")


class CommonInfoIndustry(Base):
    __tablename__ = 'common_info_industry'
    __table_args__ = {'schema': 'fastapi_schema'}

    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, unique=True)
    total_companies = Column(Integer)
    profitable_companies = Column(Integer)
    debt_free_companies = Column(Integer)
    solvent_companies = Column(Integer)
    roa_companies = Column(Integer)

    company_id = Column(Integer, ForeignKey('fastapi_schema.company_data.id'))
    company = relationship("CompanyDataORM", back_populates="industry_info")


class RegionDataORM(Base):
    __tablename__ = 'region_data'
    __table_args__ = {'schema': 'fastapi_schema'}

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, unique=True)

    total_business_value = Column(Integer)
    total_liquidation_value = Column(Integer)
    total_creditor_return = Column(Integer)
    total_working_capital_needs = Column(Integer)
    total_pre_tax_profit = Column(Integer)


class CountyDataORM(Base):
    __tablename__ = 'county_data'
    __table_args__ = {'schema': 'fastapi_schema'}

    id = Column(Integer, primary_key=True, index=True)
    county = Column(String, unique=True)

    total_business_value = Column(Integer)
    total_liquidation_value = Column(Integer)
    total_creditor_return = Column(Integer)
    total_working_capital_needs = Column(Integer)
    total_pre_tax_profit = Column(Integer)