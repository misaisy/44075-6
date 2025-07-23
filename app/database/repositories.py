import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import CompanyDataORM, RegionDataORM, CountyDataORM, CommonInfoRegion, CommonInfoCounty, \
    CommonInfoIndustry

logger = logging.getLogger(__name__)


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def clear_all_data(self) -> None:
        """Очищает все данные из таблицы CompanyDataORM"""
        try:
            self.db.query(CompanyDataORM).delete()
            self.db.commit()
            logger.info("All data from CompanyDataORM has been cleared")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error clearing CompanyDataORM: {str(e)}")
            raise

    def create_company(self, company_data: Dict[str, Any]) -> CompanyDataORM:
        """Создает новую запись компании"""
        try:
            bankruptcy_key = "возбуждено производство по делу о несостоятельности (банкротстве)"
            main_data = {}
            bankruptcy_data = {}

            for key, value in company_data.items():
                if bankruptcy_key in key or list(company_data.keys()).index(key) >= list(company_data.keys()).index(
                        bankruptcy_key):
                    bankruptcy_data[key] = value
                else:
                    main_data[key] = value

            db_company = CompanyDataORM(**main_data, bankruptcy_data=bankruptcy_data)
            self.db.add(db_company)
            self.db.commit()
            self.db.refresh(db_company)
            logger.debug(f"Created company with ID: {db_company.id}")
            return db_company
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating company: {str(e)}")
            raise

    def bulk_create_companies(self, companies_data: List[Dict[str, Any]]) -> int:
        """Массовое создание компаний с автоматической агрегацией"""
        try:
            self.clear_all_data()
            created_count = 0

            for company_data in companies_data:
                self.create_company(company_data)
                created_count += 1

            self._update_aggregated_data()
            self._update_common_info()  # Добавляем вызов обновления общей информации

            logger.info(f"Successfully created {created_count} companies")
            return created_count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error in bulk company creation: {str(e)}")
            raise

    def _update_common_info(self):
        """Обновляет общую информацию по регионам, округам и отраслям"""
        try:
            # Очищаем старые данные
            self.db.query(CommonInfoRegion).delete()
            self.db.query(CommonInfoCounty).delete()
            self.db.query(CommonInfoIndustry).delete()

            # Обновляем данные по регионам
            self._update_common_info_region()

            # Обновляем данные по округам
            self._update_common_info_county()

            # Обновляем данные по отраслям
            self._update_common_info_industry()

            self.db.commit()
            logger.info("Common info tables updated successfully")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating common info: {str(e)}")
            raise

    def _update_common_info_region(self):
        """Обновляет CommonInfoRegion"""
        region_stats = self.db.execute(text("""
            SELECT 
                region,
                COUNT(*) as total_companies,
                SUM(CASE WHEN (bankruptcy_data->>'pre_tax_profit')::INTEGER > 0 THEN 1 ELSE 0 END) as profitable_companies,
                SUM(CASE WHEN (bankruptcy_data->>'creditor_return')::INTEGER = 0 THEN 1 ELSE 0 END) as debt_free_companies,
                SUM(CASE WHEN (bankruptcy_data->>'solvency_rank')::INTEGER > 0 THEN 1 ELSE 0 END) as solvent_companies,
                SUM(CASE WHEN (bankruptcy_data->>'roa_coefficient')::FLOAT != 0 THEN 1 ELSE 0 END) as roa_companies
            FROM fastapi_schema.company_data
            GROUP BY region
        """)).fetchall()

        for stat in region_stats:
            common_info = CommonInfoRegion(
                region=stat.region,
                total_companies=stat.total_companies,
                profitable_companies=stat.profitable_companies,
                debt_free_companies=stat.debt_free_companies,
                solvent_companies=stat.solvent_companies,
                roa_companies=stat.roa_companies
            )
            self.db.add(common_info)

    def _update_common_info_county(self):
        """Обновляет CommonInfoCounty"""
        county_stats = self.db.execute(text("""
            SELECT 
                CASE
                    WHEN region = 'Москва' THEN 'Центральный'
                    WHEN region = 'СПб' THEN 'Северо-Западный'
                    WHEN region = 'Новосибирск' THEN 'Сибирский'
                    ELSE 'Другой'
                END as county,
                COUNT(*) as total_companies,
                SUM(CASE WHEN (bankruptcy_data->>'pre_tax_profit')::INTEGER > 0 THEN 1 ELSE 0 END) as profitable_companies,
                SUM(CASE WHEN (bankruptcy_data->>'creditor_return')::INTEGER = 0 THEN 1 ELSE 0 END) as debt_free_companies,
                SUM(CASE WHEN (bankruptcy_data->>'solvency_rank')::INTEGER > 0 THEN 1 ELSE 0 END) as solvent_companies,
                SUM(CASE WHEN (bankruptcy_data->>'roa_coefficient')::FLOAT != 0 THEN 1 ELSE 0 END) as roa_companies
            FROM fastapi_schema.company_data
            GROUP BY county
        """)).fetchall()

        for stat in county_stats:
            common_info = CommonInfoCounty(
                county=stat.county,
                total_companies=stat.total_companies,
                profitable_companies=stat.profitable_companies,
                debt_free_companies=stat.debt_free_companies,
                solvent_companies=stat.solvent_companies,
                roa_companies=stat.roa_companies
            )
            self.db.add(common_info)

    def _update_common_info_industry(self):
        """Обновляет CommonInfoIndustry"""
        industry_stats = self.db.execute(text("""
            SELECT 
                industry,
                COUNT(*) as total_companies,
                SUM(CASE WHEN (bankruptcy_data->>'pre_tax_profit')::INTEGER > 0 THEN 1 ELSE 0 END) as profitable_companies,
                SUM(CASE WHEN (bankruptcy_data->>'creditor_return')::INTEGER = 0 THEN 1 ELSE 0 END) as debt_free_companies,
                SUM(CASE WHEN (bankruptcy_data->>'solvency_rank')::INTEGER > 0 THEN 1 ELSE 0 END) as solvent_companies,
                SUM(CASE WHEN (bankruptcy_data->>'roa_coefficient')::FLOAT != 0 THEN 1 ELSE 0 END) as roa_companies
            FROM fastapi_schema.company_data
            GROUP BY industry
        """)).fetchall()

        for stat in industry_stats:
            common_info = CommonInfoIndustry(
                industry=stat.industry,
                total_companies=stat.total_companies,
                profitable_companies=stat.profitable_companies,
                debt_free_companies=stat.debt_free_companies,
                solvent_companies=stat.solvent_companies,
                roa_companies=stat.roa_companies
            )
            self.db.add(common_info)


    def _update_aggregated_data(self):
        """Обновляет агрегированные данные по регионам и округам"""
        try:
            self._update_region_aggregates()
            self._update_county_aggregates()
            logger.info("Aggregated data updated successfully")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating aggregated data: {str(e)}")
            raise

    def _update_region_aggregates(self):
        """Обновляет агрегированные данные по регионам"""
        self.db.query(RegionDataORM).delete()

        region_results = self.db.execute(text("""
            SELECT 
                region,
                SUM(COALESCE((bankruptcy_data->>'current_business_value')::INTEGER, 0)) as total_business_value,
                SUM(COALESCE((bankruptcy_data->>'liquidation_value')::INTEGER, 0)) as total_liquidation_value,
                SUM(COALESCE((bankruptcy_data->>'creditor_return')::INTEGER, 0)) as total_creditor_return,
                SUM(COALESCE((bankruptcy_data->>'working_capital_needs')::INTEGER, 0)) as total_working_capital_needs,
                SUM(COALESCE((bankruptcy_data->>'pre_tax_profit')::INTEGER, 0)) as total_pre_tax_profit
            FROM fastapi_schema.company_data
            GROUP BY region
            ORDER BY 
                CASE region 
                    WHEN 'Москва' THEN 1 
                    WHEN 'СПб' THEN 2 
                    WHEN 'Новосибирск' THEN 3 
                    ELSE 4 
                END
        """)).fetchall()

        for row in region_results:
            region_data = RegionDataORM(
                region=row.region,
                total_business_value=row.total_business_value,
                total_liquidation_value=row.total_liquidation_value,
                total_creditor_return=row.total_creditor_return,
                total_working_capital_needs=row.total_working_capital_needs,
                total_pre_tax_profit=row.total_pre_tax_profit
            )
            self.db.add(region_data)

        self.db.commit()

    def _update_county_aggregates(self):
        """Обновляет агрегированные данные по округам"""
        self.db.query(CountyDataORM).delete()

        county_results = self.db.execute(text("""
            SELECT 
                county,
                SUM(total_business_value) as total_business_value,
                SUM(total_liquidation_value) as total_liquidation_value,
                SUM(total_creditor_return) as total_creditor_return,
                SUM(total_working_capital_needs) as total_working_capital_needs,
                SUM(total_pre_tax_profit) as total_pre_tax_profit
            FROM (
                SELECT 
                    CASE
                        WHEN region = 'Москва' THEN 'Центральный'
                        WHEN region = 'СПб' THEN 'Северо-Западный'
                        WHEN region = 'Новосибирск' THEN 'Сибирский'
                        ELSE 'Другой'
                    END as county,
                    COALESCE((bankruptcy_data->>'current_business_value')::INTEGER, 0) as total_business_value,
                    COALESCE((bankruptcy_data->>'liquidation_value')::INTEGER, 0) as total_liquidation_value,
                    COALESCE((bankruptcy_data->>'creditor_return')::INTEGER, 0) as total_creditor_return,
                    COALESCE((bankruptcy_data->>'working_capital_needs')::INTEGER, 0) as total_working_capital_needs,
                    COALESCE((bankruptcy_data->>'pre_tax_profit')::INTEGER, 0) as total_pre_tax_profit
                FROM fastapi_schema.company_data
            ) as subquery
            GROUP BY county
            ORDER BY 
                CASE county 
                    WHEN 'Центральный' THEN 1
                    WHEN 'Северо-Западный' THEN 2 
                    WHEN 'Сибирский' THEN 3
                    ELSE 4
                END
        """)).fetchall()

        for row in county_results:
            county_data = CountyDataORM(
                county=row.county,
                total_business_value=row.total_business_value,
                total_liquidation_value=row.total_liquidation_value,
                total_creditor_return=row.total_creditor_return,
                total_working_capital_needs=row.total_working_capital_needs,
                total_pre_tax_profit=row.total_pre_tax_profit
            )
            self.db.add(county_data)

        self.db.commit()