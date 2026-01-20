from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from fastapi_app.database import SessionLocal
import fastapi_app.crud as crud
import fastapi_app.schemas as schemas
from typing import List, Optional
import io, csv
from fastapi.responses import StreamingResponse

app = FastAPI(title="Telegram Medical Analytics API")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Telegram Medical Analytics API"}
@app.get("/api/reports/top-products", response_model=List[schemas.ProductFrequency])
def read_top_products(limit: int = 10, db: Session = Depends(get_db)):
    results = crud.get_top_products(db, limit)
    return [{"product": r[0], "count": r[1]} for r in results]


@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity])
def read_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    results = crud.get_channel_activity(db, channel_name)
    return [{"date": r[0].strftime("%Y-%m-%d"), "message_count": r[1]} for r in results]


@app.get("/api/search/messages", response_model=List[schemas.SearchResult])
def search_telegram_messages(query: str, db: Session = Depends(get_db)):
    results = crud.search_messages(db, query)
    return [{"message_id": r[0], "message": r[1], "channel": r[2]} for r in results]


@app.get("/api/reports/visual-content", response_model=List[schemas.VisualContentRow])
def visual_content_report(
    channel: Optional[str] = Query(None, description="Filter by channel name"),
    limit: int = 100,
    csv_export: bool = Query(False, alias="csv", description="Return CSV when true"),
    db: Session = Depends(get_db),
):
    rows = crud.get_visual_content_report(db, channel=channel, limit=limit)

    # Convert DB rows (ResultProxy) to list of dicts/objects
    results = []
    for r in rows:
        results.append({
            "detection_id": r[0],
            "message_id": r[1],
            "object_class": r[2],
            "confidence": float(r[3]) if r[3] is not None else None,
            "message": r[4],
            "channel": r[5],
            "date": r[6].strftime("%Y-%m-%d") if r[6] is not None else None,
        })

    if csv_export:
        # stream CSV back
        def iter_csv():
            sio = io.StringIO()
            writer = csv.writer(sio)
            writer.writerow(["detection_id","message_id","object_class","confidence","message","channel","date"])
            yield sio.getvalue()
            sio.seek(0); sio.truncate(0)
            for r in results:
                writer.writerow([r["detection_id"], r["message_id"], r["object_class"], r["confidence"], r["message"], r["channel"], r["date"]])
                yield sio.getvalue()
                sio.seek(0); sio.truncate(0)

        headers = {"Content-Disposition": "attachment; filename=visual_content_report.csv"}
        return StreamingResponse(iter_csv(), media_type="text/csv", headers=headers)

    return results