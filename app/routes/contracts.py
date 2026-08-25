import os
import uuid

from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_DIR
from database import contract_collection
from fastapi import APIRouter, File, HTTPException, UploadFile
from models import Contract
from service.document_parser import extract_text

router = APIRouter(
    prefix="/contracts",
    tags=["contracts"],
)

@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} is not allowed")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds limit")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    parsed = extract_text(file_path)

    contract_data = Contract(
        filename=unique_name,
        original_name=file.filename or unique_name,
        file_path=file_path,
        text=parsed["text"],
        text_count=parsed["text_count"],
        word_count=parsed["word_count"],
        page_count=parsed["page_count"],
    )
    doc = contract_data.model_dump(exclude={"id"})
    result = contract_collection.insert_one(doc)
    contract_data.id = str(result.inserted_id)

    return {
        "message": "Contract uploaded successfully",
        "id": contract_data.id,
        "contract": contract_data.model_dump(),
    }


@router.get("/")
async def list_contract():
    contracts = []
    for doc in contract_collection.find():
        contract = Contract(**doc)
        contract.id = str(doc["_id"])
        contracts.append(contract.model_dump())
    return {"contracts": contracts}


@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    from bson import ObjectId
    doc = contract_collection.find_one({"_id": ObjectId(contract_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Contract not found")
    contract = Contract(**doc)
    contract.id = str(doc["_id"])

    return {"contract": contract.model_dump()}
