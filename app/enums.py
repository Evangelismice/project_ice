import enum


class Gender(str, enum.Enum):
    male = 'male'
    female = 'female'


class Department(str, enum.Enum):
    executive = 'executive'
    school_of_evangelism = 'school_of_evangelism'
    operations = 'operations'
    ministry_team = 'ministry_team'
    kitchen = 'kitchen'
    grounds = 'grounds'
    security = 'security'


class StaffStatus(str, enum.Enum):
    active = 'active'
    on_leave = 'on_leave'
    resigned = 'resigned'
    retired = 'retired'


class DonorType(str, enum.Enum):
    individual = 'individual'
    church = 'church'
    organization = 'organization'


class PaymentMethod(str, enum.Enum):
    cash = 'cash'
    bank_transfer = 'bank_transfer'
    cheque = 'cheque'
    online = 'online'


class MemberType(str, enum.Enum):
    member = 'member'
    partner = 'partner'
    volunteer = 'volunteer'
