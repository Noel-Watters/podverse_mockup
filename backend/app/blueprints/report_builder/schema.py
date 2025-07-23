from marshmallow import Schema, fields, validate

class CustomReportSchema(Schema):
    source = fields.Str(required=True, validate=validate.OneOf([
        "channels", "feeds", "stats_items", "stats_channels"
    ])) # Tells the query builder what model/schema/table needs to be accessed
    selected_fields = fields.List(fields.Str(), required=True)
    filters = fields.Dict(keys=fields.Str(), values=fields.Raw(), missing={})
    format = fields.Str(required=True, validate=validate.OneOf(["csv", "json"]))
    export_by = fields.Email(required=True)
