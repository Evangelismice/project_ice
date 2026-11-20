import enum
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.base import Base
from ..models.donors import Donor
from ..models.donations import Donation
from ..models.staffs import Staff
from ..models.members import Member
from ..auth.jwt import get_current_user

router = APIRouter(prefix='/reports', tags=['Reports'], dependencies=[Depends(get_current_user)])


@router.get('/summary')
def summary(db: Session = Depends(get_db)):
    months = defaultdict(lambda: {'total': Decimal(0), 'count': 0})
    per_donor = defaultdict(Decimal)
    for d in db.query(Donation).all():
        key = d.date_received.strftime('%Y-%m')
        months[key]['total'] += d.amount
        months[key]['count'] += 1
        per_donor[d.donor_id] += d.amount
    names = {d.id: d.name for d in db.query(Donor).all()}
    top = sorted(per_donor.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        'donations_by_month': [{'month': k, 'total': float(v['total']), 'count': v['count']}
                               for k, v in sorted(months.items(), reverse=True)],
        'top_donors': [{'name': names.get(i, f'#{i}'), 'total': float(t)} for i, t in top],
        'staff_by_department': [{'department': dep.value, 'count': n} for dep, n in
                                db.query(Staff.department, func.count(Staff.id)).group_by(Staff.department).all()],
        'members_by_type': [{'member_type': t.value, 'count': n} for t, n in
                            db.query(Member.member_type, func.count(Member.id)).group_by(Member.member_type).all()],
    }


def _json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, enum.Enum):
        return value.value
    return value


@router.get('/backup')
def backup(db: Session = Depends(get_db)):
    """Download every table as one JSON file (user accounts are left out on purpose)."""
    data = {}
    for table in Base.metadata.sorted_tables:
        if table.name == 'users':
            continue
        data[table.name] = [{k: _json_safe(v) for k, v in row._mapping.items()} for row in db.execute(table.select())]
    return JSONResponse(data, headers={'Content-Disposition': f'attachment; filename=ice-backup-{date.today()}.json'})
