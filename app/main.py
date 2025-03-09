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

def get_compass_direction(degrees: float) -> str:
    # Define the eight cardinal and intercardinal directions
    compass = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    # Adjust by 22.5 degrees for rounding and compute the index
    index = int((degrees + 22.5) % 360 // 45)
    return compass[index]


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

@app.get("/active_claim_at_point")
def active_claim_at_point(lat: float = Query(...), lon: float = Query(...), db: Session = Depends(get_db)):
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


@app.get("/district_search")
def district_search(
        lat: float = Query(...),
        lon: float = Query(...),
        radius: float = Query(1000, description="Search radius in meters"),
        db: Session = Depends(get_db)
):
    point_geo = transform_point(lat, lon)

    query = db.query(
        MiningDistrict,
        func.ST_Contains(MiningDistrict.geom, point_geo).label("contains"),
        func.ST_Distance(MiningDistrict.geom, point_geo).label("distance"),
        func.degrees(func.ST_Azimuth(point_geo, func.ST_Centroid(MiningDistrict.geom))).label("direction")
    ).filter(
        func.ST_DWithin(MiningDistrict.geom, point_geo, radius)
    )
    results = query.all()

    return [
        {
            "id": district.id,
            "district": district.district,
            "webpage": district.webpage,
            "contains": bool(contains),
            "distance_meters": distance,
            "direction_degrees": get_compass_direction(direction)
        }
        for district, contains, distance, direction in results
    ]


@app.get("/active_claim_search")
def active_claim_search(
        lat: float = Query(...),
        lon: float = Query(...),
        radius: float = Query(1000, description="Search radius in meters"),
        db: Session = Depends(get_db)
):
    point_geo = transform_point(lat, lon)

    query = db.query(
        ActiveClaims,
        func.ST_Contains(ActiveClaims.geom, point_geo).label("contains"),
        func.ST_Distance(ActiveClaims.geom, point_geo).label("distance"),
        func.degrees(func.ST_Azimuth(point_geo, func.ST_Centroid(ActiveClaims.geom))).label("direction")
    ).filter(
        func.ST_DWithin(ActiveClaims.geom, point_geo, radius)
    )
    results = query.all()

    return [
        {
            "gid": claim.gid,
            "serial_no": claim.serial_no,
            "claim_nm": claim.claim_nm,
            "commodity": claim.commodity,
            "acres": claim.case_acres,
            "names": [claim.name_1, claim.name_2, claim.name_3, claim.name_4],
            "contains": bool(contains),
            "distance_meters": distance,
            "direction_degrees": get_compass_direction(direction)
        }
        for claim, contains, distance, direction in results
    ]


@app.get("/inactive_claim_search")
def inactive_claim_search(
        lat: float = Query(...),
        lon: float = Query(...),
        radius: float = Query(1000, description="Search radius in meters"),
        db: Session = Depends(get_db)
):
    point_geo = transform_point(lat, lon)

    query = db.query(
        InactiveClaims,
        func.ST_Contains(InactiveClaims.geom, point_geo).label("contains"),
        func.ST_Distance(InactiveClaims.geom, point_geo).label("distance"),
        func.degrees(func.ST_Azimuth(point_geo, func.ST_Centroid(InactiveClaims.geom))).label("direction")
    ).filter(
        func.ST_DWithin(InactiveClaims.geom, point_geo, radius)
    )
    results = query.all()

    return [
        {
            "gid": claim.gid,
            "serial_no": claim.serial_no,
            "claim_nm": claim.claim_nm,
            "commodity": claim.commodity,
            "acres": claim.case_acres,
            "names": [claim.name_1, claim.name_2, claim.name_3, claim.name_4],
            "locate_dt": claim.locate_dt,
            "contains": bool(contains),
            "distance_meters": distance,
            "direction_degrees": get_compass_direction(direction)
        }
        for claim, contains, distance, direction in results
    ]
