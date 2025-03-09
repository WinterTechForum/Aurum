# app/main.py
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


@app.get("/lookup")
def district_lookup(lat: float = Query(...), lon: float = Query(...), db: Session = Depends(get_db)):
    source_crs = CRS.from_epsg(4326)  # WGS84 lat/lon
    target_crs = CRS.from_epsg(26913)  # NAD83 / UTM zone 13N
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    point_utm = Point(x, y)

    # Create a Shapely point (note that GeoAlchemy2 expects (longitude, latitude))
    # point = from_shape(Point(lon, lat), srid=4326)

    point_geo = from_shape(point_utm, srid=26913)

    # Query for a mining district that contains the point
    district = db.query(MiningDistrict).filter(
        func.ST_Contains(MiningDistrict.geom, point_geo)
    ).first()

    if not district:
        raise HTTPException(status_code=404, detail="No mining district found for the given point.")

    return {
        "name": district.district,
        "info": district.webpage,
    }

@app.get("/claim_lookup")
def claim_lookup(lat: float = Query(...), lon: float = Query(...), db: Session = Depends(get_db)):
    source_crs = CRS.from_epsg(4326)  # WGS84 lat/lon
    target_crs = CRS.from_epsg(26913)  # NAD83 / UTM zone 13N
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    point_utm = Point(x, y)

    # Create a Shapely point (note that GeoAlchemy2 expects (longitude, latitude))
    # point = from_shape(Point(lon, lat), srid=4326)

    point_geo = from_shape(point_utm, srid=26913)

    # Query for a mining district that contains the point
    claim: ActiveClaims = db.query(ActiveClaims).filter(
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
    }

@app.get("/inactive_claim_lookup")
def inactive_claim_lookup(lat: float = Query(...), lon: float = Query(...), db: Session = Depends(get_db)):
    source_crs = CRS.from_epsg(4326)  # WGS84 lat/lon
    target_crs = CRS.from_epsg(26913)  # NAD83 / UTM zone 13N
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    point_utm = Point(x, y)

    # Create a Shapely point (note that GeoAlchemy2 expects (longitude, latitude))
    # point = from_shape(Point(lon, lat), srid=4326)

    point_geo = from_shape(point_utm, srid=26913)

    # Query for a mining district that contains the point
    claim: ActiveClaims = db.query(InactiveClaims).filter(
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
