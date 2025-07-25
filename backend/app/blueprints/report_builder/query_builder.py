from app.models import Channel, Feed, StatsAggregatedItem, StatsAggregatedChannel
#from sqlalchemy.orm import load_only
from sqlalchemy import and_
from app.extensions import db

# Define lookup map for SQLAlchemy Models
MODEL_MAP = {
    "channels": Channel,
    "feeds": Feed,
    "stats_items": StatsAggregatedItem,
    "stats_channels": StatsAggregatedChannel
}

# Define supported operators for comparison
OPERATORS = {
    "__gt": lambda col, val: col > val, # Greater Than
    "__lt": lambda col, val: col < val, # Less than
    "__gte": lambda col, val: col >= val, # Greater Than or Equal to
    "__lte": lambda col, val: col <= val, # Less than or equal to
    "__eq": lambda col, val: col == val, # Equal to
    "__ne": lambda col, val: col != val, # Not Equal to
    "__ilike": lambda col, val: col.ilike(f"%{val}%"), # Like search for channel titles, etc
}

def build_dynamic_query(source, fields, filters, db_session):
    Model = MODEL_MAP.get(source)
    if not Model:
        raise ValueError("Invalid Source")
    
    #query = db_session.query(Model).options(load_only(*fields))
    query = db_session.query(Model)

    conditions = []
    for operator, value in filters.items():
        for suffix, op in OPERATORS.items():
            if operator.endswith(suffix):
                field = operator[:-len(suffix)]
                col = getattr(Model, field, None)
                if col is not None:
                    conditions.append(op(col, value))
                break
        else:
            # default to checking equality
            col = getattr(Model, operator, None)
            if col is not None:
                conditions.append(col == value)

    if conditions:
        query = query.filter(and_(*conditions))
    
    return query