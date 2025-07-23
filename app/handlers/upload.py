import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from app.database.repositories import CompanyRepository
from app.database.session import get_db
from app.utils.csv_processor import process_csv_file

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    """Загружает CSV файл и сохраняет данные в БД"""
    try:
        logger.info(f"Starting CSV upload process for file: {file.filename}")

        if not file.filename.endswith('.csv'):
            error_msg = "File must be a CSV"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        logger.debug("Processing CSV file")
        companies_data = await process_csv_file(file)

        db = next(get_db())
        repo = CompanyRepository(db)
        created_count = repo.bulk_create_companies(companies_data)

        logger.info(f"Successfully uploaded {created_count} records")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": f"Successfully uploaded {created_count} records"}
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing CSV file: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)