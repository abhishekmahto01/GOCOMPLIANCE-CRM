"""API endpoints for Sales Bulk Import, Template Download, Validation, and Bulk Assignment."""
import io
import uuid
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.sales_import import (
    SalesImportExecuteRequest,
    SalesImportExecuteResponse,
    SalesImportPreviewResponse,
    SalesImportRowValidation,
)
from app.services import permissions, sales_import_service

router = APIRouter(prefix="/sales/import", tags=["Sales Bulk Import"])


def _verify_sales_access(session: Session, user: User, action: str = "view") -> None:
    """Verify actor has permission to access or create sales orders."""
    if permissions.is_super_admin_user(session, user):
        return

    has_access = False
    for mod in ("SALES_CONFIRMED_ORDER", "SALES", "SALES_ALL_ORDERS", "SALES_MY_ORDERS"):
        if permissions.has_permission(session, user, mod, action):
            has_access = True
            break

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. You do not have '{action}' permission for Sales modules.",
        )


@router.get(
    "/template/xlsx",
    summary="Download Excel Master Template",
    description="Download the official Excel (.xlsx) master import template with instructions and formatted columns.",
    response_class=Response,
)
def download_xlsx_template(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> Response:
    """Generate and return master Excel template."""
    _verify_sales_access(session, current_user, "view")
    content = sales_import_service.generate_master_template_xlsx(session=session)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="sales_import_master_template.xlsx"'},
    )


@router.get(
    "/template/csv",
    summary="Download CSV Master Template",
    description="Download the official CSV master import template with exact column headers.",
    response_class=Response,
)
def download_csv_template(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> Response:
    """Generate and return master CSV template."""
    _verify_sales_access(session, current_user, "view")
    content = sales_import_service.generate_master_template_csv()
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="sales_import_master_template.csv"'},
    )


@router.post(
    "/preview",
    response_model=SalesImportPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate and Preview Sales Import File",
    description="Upload Excel or CSV file to validate all rows, detect duplicates, and preview records before importing. No records are created.",
)
async def preview_sales_import(
    file: UploadFile = File(...),
    apply_gst: bool = Query(False, description="Whether to calculate 18% GST on uploaded amounts"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesImportPreviewResponse:
    """Upload and validate sales file without creating database records."""
    _verify_sales_access(session, current_user, "view")

    filename = file.filename or "uploaded_sales_file"
    if not (
        filename.lower().endswith(".xlsx")
        or filename.lower().endswith(".csv")
        or filename.lower().endswith(".numbers")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{filename}'. Only .xlsx, .csv, and .numbers files are supported.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    try:
        preview = sales_import_service.parse_and_validate_sales_file(
            file_bytes=file_bytes,
            filename=filename,
            current_user=current_user,
            session=session,
            apply_gst=apply_gst,
        )
        return preview
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing file: {str(exc)}",
        )


@router.post(
    "/error-report",
    summary="Download Import Validation Error Report",
    description="Download a detailed CSV report of row-by-row validation errors and duplicate warnings.",
    response_class=Response,
)
def download_error_report(
    rows: List[SalesImportRowValidation],
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> Response:
    """Generate and return CSV error report for validated rows."""
    _verify_sales_access(session, current_user, "view")
    csv_bytes = sales_import_service.generate_validation_error_csv(rows)
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="sales_import_validation_errors.csv"'},
    )


@router.post(
    "/execute",
    response_model=SalesImportExecuteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Atomically Import and Bulk Assign Sales Orders",
    description="Atomically create sales orders and assign them to the selected Operations assignee. Rolls back if any row or assignment fails.",
)
def execute_bulk_import(
    data: SalesImportExecuteRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SalesImportExecuteResponse:
    """Atomically commit all sales entries and Operations assignments in a single transaction."""
    _verify_sales_access(session, current_user, "create")

    try:
        result = sales_import_service.execute_bulk_sales_import(
            session=session,
            current_user=current_user,
            data=data,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during bulk import: {str(exc)}",
        )
