"""Pinned EPSG Amersfoort to WGS84 (4) Helmert operation; never downloads grids."""
import hashlib
from .catalog import DATA,read
from pyproj import CRS, Transformer, database, network, __proj_version__, __version__
network.set_network_enabled(False)
PIPELINE = ('+proj=pipeline +step +inv +proj=sterea +lat_0=52.1561605555556 '
 '+lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel '
 '+step +proj=push +v_3 +step +proj=cart +ellps=bessel '
 '+step +proj=helmert +x=565.4171 +y=50.3319 +z=465.5524 '
 '+rx=0.398957388243134 +ry=-0.343987817378283 +rz=1.87740163998045 '
 '+s=4.0725 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 '
 '+step +proj=pop +v_3 +step +proj=unitconvert +xy_in=rad +xy_out=deg')
TRANSFORMER=Transformer.from_pipeline(PIPELINE)


def normalize_rd(raw,crs):
    if crs=='EPSG:28991':return [raw[0]+155000,raw[1]+463000]
    if crs=='EPSG:28992':return list(raw)
    raise ValueError('Unverified projected CRS')


def convert(rd):
    if not (0<=rd[0]<=300000 and 280000<=rd[1]<=630000):
        raise ValueError('RD coordinate outside pilot geographic envelope: check axes, units and origin')
    return list(TRANSFORMER.transform(*rd,errcheck=True))


def definition():
    supplied=DATA/'crs/epsg-28992.json'
    if not CRS.from_json(supplied.read_text()).equals(CRS.from_epsg(28992),ignore_axis_order=False):
        raise ValueError('Supplied CRS differs from EPSG:28992')
    return {'sourceCrs':'EPSG:28992','targetCrs':'OGC:CRS84','axisOrder':['longitude','latitude'],
            'operation':'Inverse of RD New + Amersfoort to WGS 84 (4), EPSG:4833',
            'accuracyMetres':1,'pipeline':PIPELINE,'gridFiles':[], 'networkEnabled':False,
            'ballpark':False,'suppliedDefinitionUrl':'https://epsg.io/28992.json','suppliedDefinitionSha256':hashlib.sha256(supplied.read_bytes()).hexdigest(),'pyprojVersion':__version__,'projVersion':__proj_version__,
            'epsgVersion':database.get_database_metadata('EPSG.VERSION'),
            'sourceDefinition':CRS.from_epsg(28992).to_json_dict(),
            'rdOldDefinition':CRS.from_epsg(28991).to_json_dict(),
            'rdOldNormalization':{'offsetMetres':[155000,463000],
             'reason':'Same Amersfoort oblique stereographic conversion; different false origin. Applied only after signed border-label review.'}}
