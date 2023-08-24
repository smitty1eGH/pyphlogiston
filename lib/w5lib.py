from enum import IntEnum

DEFAULT='__default__'
LRU_SUFF='_lru'

# These are related, but we'll violate DRY momentarily
wtypes={'what':0,'who':1,'where_':2,'when_':3,'why':4,0:'what',1:'who',2:'where_',3:'when_',4:'why'}
class WType(IntEnum):
    """Storage schema types."""

    what = 0
    who = 1
    where_ = 2
    when_ = 3
    why = 4

class DType(IntEnum):
    """Types used to decode the data payloads for the records."""

    whoBase = 0
    whoExtended = 1
    whoImages = 2
    whereBase = 3
    whereExtended = 4
    whenBorn = 5
    whenDied = 6
    whenStart = 7
    whenStop = 8

dtype2table = {
    DType.whoBase.value : 'who',
    DType.whoExtended.value : 'who',
    DType.whoImages.value : 'who',
    DType.whereBase.value : 'where',
    DType.whereExtended.value : 'where',
    DType.whenBorn.value : 'when',
    DType.whenDied.value : 'when',
    DType.whenStart.value : 'when',
    DType.whenStop.value : 'when'}
