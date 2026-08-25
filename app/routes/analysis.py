from bson import ObjectId
from config import GEMINI_API_KEY
from database import analysis_collection, contract_collection
from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from service.gemini_analysis import analyze_contract as run_analysis

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


def _serialize_analysis_doc(doc: dict) -> dict:
    serialized = dict(doc)
    if "_id" in serialized:
        serialized["_id"] = str(serialized["_id"])
    return serialized


@router.post("/")
async def create_analysis(contract_id: str):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")

    try:
        object_id = ObjectId(contract_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid contract id") from exc

    contract = contract_collection.find_one({"_id": object_id})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    text_content = contract.get("text") or contract.get("text_content")
    if not text_content:
        raise HTTPException(status_code=400, detail="Contract text content not found")

    contract_collection.update_one(
        {"_id": object_id},
        {"$set": {"analysis_status": "in_progress"}},
    )

    try:
        result = await run_analysis(contract_id, text_content)
        doc = result.model_dump()

        existing = analysis_collection.find_one(
            {"contract_id": contract_id},
            {"_id": 1},
        )
        if existing:
            doc["_id"] = existing["_id"]
            analysis_collection.replace_one({"_id": existing["_id"]}, doc)
            result.id = str(existing["_id"])
        else:
            insert_result = analysis_collection.insert_one(doc)
            result.id = str(insert_result.inserted_id)

        contract_collection.update_one(
            {"_id": object_id},
            {"$set": {"analysis_status": "completed"}},
        )

        return {
            "message": "Contract analysis completed successfully",
            "analysis": result.model_dump(),
            "id": result.id,
        }
    except HTTPException:
        contract_collection.update_one(
            {"_id": object_id},
            {"$set": {"analysis_status": "failed"}},
        )
        raise
    except (RuntimeError, ValueError) as exc:
        contract_collection.update_one(
            {"_id": object_id},
            {"$set": {"analysis_status": "failed"}},
        )
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except PyMongoError as exc:
        contract_collection.update_one(
            {"_id": object_id},
            {"$set": {"analysis_status": "failed"}},
        )
        raise HTTPException(status_code=500, detail=f"Database error: {exc}") from exc
    except Exception as exc:
        contract_collection.update_one(
            {"_id": object_id},
            {"$set": {"analysis_status": "failed"}},
        )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str):
    try:
        object_id = ObjectId(analysis_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid analysis id") from exc

    analysis = analysis_collection.find_one({"_id": object_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysis": _serialize_analysis_doc(analysis)
    }

@router.get("/")
def list_analyses():
    analyses = []
    for doc in analysis_collection.find():
        analyses.append(_serialize_analysis_doc(doc))
    return {
        "analyses": analyses
    }


@router.get("/contract/{contract_id}")
async def get_analyses_for_contract(contract_id: str):
    analyses = []
    for doc in analysis_collection.find({"contract_id": contract_id}):
        analyses.append(_serialize_analysis_doc(doc))
    return {
        "analyses": analyses
    }
