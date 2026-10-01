from fastapi import APIRouter

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


@router.get("/{parcel_id}")
def get_analysis(parcel_id: str):
    return {
        "parcel_id": parcel_id,
        "message": (
            "Use /api/cadastral/comparison/{run_id} "
            "for cadastral comparison results."
        ),
    }


@router.post("/{parcel_id}/compare")
def compare_analysis(parcel_id: str):
    return {
        "parcel_id": parcel_id,
        "message": (
            "Use /api/cadastral/compare for "
            "old/new layer comparison."
        ),
    }
