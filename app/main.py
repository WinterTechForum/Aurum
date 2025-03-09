from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from sqlalchemy import func
from pyproj import CRS, Transformer


from app.database import SessionLocal, engine
from app.models import Base, MiningDistrict, ActiveClaims, InactiveClaims

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mining District API")


# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def transform_point(lat: float, lon: float) -> 'Geometry':
    # Convert from WGS84 (EPSG:4326) to NAD83 / UTM zone 13N (EPSG:26913)
    source_crs = CRS.from_epsg(4326)
    target_crs = CRS.from_epsg(26913)
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    point_utm = Point(x, y)
    return from_shape(point_utm, srid=26913)


@app.get("/district_at_point")
def district_at_point(lat: float = Query(...), lon: float = Query(...), db: Session = Depends(get_db)):
    point_geo = transform_point(lat, lon)

    # Query for a mining district that contains the point
    district: MiningDistrict|None = db.query(MiningDistrict).filter(
        func.ST_Contains(MiningDistrict.geom, point_geo)
    ).first()

    if not district:
        raise HTTPException(status_code=404, detail="No mining district found for the given point.")

    return {
        "name": district.district,
        "info": district.webpage,
    }

@app.get("/claim_at_point")
def claim_at_point(lat: float = Query(...), lon: float = Query(...), db: Session = Depends(get_db)):
    point_geo = transform_point(lat, lon)

    # Query for a mining district that contains the point
    claim: ActiveClaims|None = db.query(ActiveClaims).filter(
        func.ST_Contains(ActiveClaims.geom, point_geo)
    ).first()

    if not claim:
        raise HTTPException(status_code=404, detail="No active claim found for the given point.")

    return {
        "name": claim.claim_nm,
        "commodity": claim.commodity,
        "acres": claim.case_acres,
        "name_1": claim.name_1,
        "name_2": claim.name_2,
        "name_3": claim.name_3,
        "name_4": claim.name_4,
        "location_date": claim.locate_dt,
    }

@app.get("/inactive_claim_at_point")
def inactive_claim_at_point(lat: float = Query(...), lon: float = Query(...), db: Session = Depends(get_db)):
    point_geo = transform_point(lat, lon)

    # Query for a mining district that contains the point
    claim: InactiveClaims|None = db.query(InactiveClaims).filter(
        func.ST_Contains(InactiveClaims.geom, point_geo)
    ).first()

    if not claim:
        raise HTTPException(status_code=404, detail="No inactive claim found for the given point.")

    return {
        "name": claim.claim_nm,
        "commodity": claim.commodity,
        "acres": claim.case_acres,
        "name_1": claim.name_1,
        "name_2": claim.name_2,
        "name_3": claim.name_3,
        "name_4": claim.name_4,
        "location_date": claim.locate_dt,
    }
