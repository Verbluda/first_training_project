from marshmallow import Schema, fields, validate


class PolzovatelSchema(Schema):
    email = fields.Email(required=True)
    reg_date = fields.DateTime(required=True)
    points = fields.Int(required=True, validate=validate.Range(min=1))
    fav_hospital = fields.Int(required=False)

class PolzovatelPatchSchema(Schema):
    email = fields.Email(required=False)
    reg_date = fields.DateTime(required=False)
    points = fields.Int(required=False, validate=validate.Range(min=1))
    fav_hospital = fields.Int(required=False)

class PolzovatelSchemaPoints(Schema):
    points = fields.Int(required=True, validate=validate.Range(min=0))

class PolzovatelSchemaPointsGTE(Schema):
    points_gte = fields.Int(required=True, validate=validate.Range(min=0))

class HospitalSchemaCity(Schema):
    city = fields.String(required=True)

class HospitalSchemaDoctorCountLTE(Schema):
    doctor_count_lte = fields.Int(required=True, validate=validate.Range(min=0))

class HospitalSchema(Schema):
    name = fields.String(required=True)
    city = fields.String(required=True)
    adress = fields.String(required=True)
    doctor_count = fields.Int(required=True, validate=validate.Range(min=0))
