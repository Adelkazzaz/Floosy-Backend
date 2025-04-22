from fastapi import APIRouter, Depends
from app.services.admin_service import AdminService
from app.api.dependencies import get_admin_service, get_current_admin
from app.models.user import UserInDB

router = APIRouter()

@router.get("/admin/stats")
async def get_admin_stats(
    current_user: UserInDB = Depends(get_current_admin),
    admin_service: AdminService = Depends(get_admin_service)
):
    stats = await admin_service.get_admin_dashboard_stats()
    return {
        "success": True,
        "data": stats
    }
