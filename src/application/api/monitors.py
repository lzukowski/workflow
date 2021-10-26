from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", name="monitors:ping")
async def ping():
    pass
