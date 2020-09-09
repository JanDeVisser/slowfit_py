from ..models.fits import Visit

VISIT_DATE = "2020-09-01 09:00:00"
VISIT_PURPOSE = "Testy wants to get riding"
VISIT_EXPERIENCE = "Testy has seen a bike before"
VISIT_GOALS = "Be able to ride to the pub"
VISIT_INJURIES = "Testy is healthy"
VISIT_WEIGHT = 0
VISIT_CUSTOMER_CONCERNS = "Cycling is difficult"
VISIT_FITTER_CONCERNS = "He's gonna be fine"
VISIT_CURRENTBIKE = ""
VISIT_PEDALSYSTEM = "Look"
VISIT_HX = 514
VISIT_HY = 640
VISIT_SX = 700
VISIT_SY = 0
VISIT_CRANKLENGTH = 170
VISIT_SADDLE = "Fizik Antares"
VISIT_SADDLEHEIGHT = 795
VISIT_SADDLESETBACK = 30
VISIT_SADDLEBARDROP = 150

VISIT_DATA = {
    "date": VISIT_DATE,
    "purpose": VISIT_PURPOSE,
    "experience": VISIT_EXPERIENCE,
    "goals": VISIT_GOALS,
    "injuries": VISIT_INJURIES,
    "weight": VISIT_WEIGHT,
    "customerConcerns": VISIT_CUSTOMER_CONCERNS,
    "fitterConcerns": VISIT_FITTER_CONCERNS,
    "currentBike": VISIT_CURRENTBIKE,
    "pedalSystem": VISIT_PEDALSYSTEM,
    "hx": VISIT_HX,
    "hy": VISIT_HY,
    "sx": VISIT_SX,
    "sy": VISIT_SY,
    "crankLength": VISIT_CRANKLENGTH,
    "saddle": VISIT_SADDLE,
    "saddleHeight": VISIT_SADDLEHEIGHT,
    "saddleSetback": VISIT_SADDLESETBACK,
    "saddleBarDrop": VISIT_SADDLEBARDROP,
}


def create_visit(customer_id):
    kwargs = dict(VISIT_DATA)
    kwargs["customer_id"] = customer_id
    kwargs["currentBike"] = None
    visit = Visit(**kwargs)
    visit.save()
    return visit.id
