import logging
import math

from django.http import HttpResponseServerError
from django.http import JsonResponse

from .models.bikes import Brand, Frame, FrameSize

logger = logging.getLogger(__name__)

stem_angles = [-17, -6, 6, 17]

# stem_lengths = [ 70, 80, 90, 95, 100, 105, 110, 120, 130, 140 ]
stem_lengths = [70, 80, 90, 95, 100, 105, 110, 120, 130]

AllResults = "ALL"
OnlyBest = "ONLYBEST"


class ParameterMissing(Exception):
    def __init__(self, param):
        self.param = param

    def __str__(self):
        return f"Parameter:self.param missing"


def int_value(request, name):
    string_value = request.GET.get(name)
    if string_value is None:
        raise ParameterMissing(name)
    return int(string_value)


def optional_int_value(request, name, default_value):
    string_value = request.GET.get(name)
    if string_value is None:
        return default_value
    return int(string_value)


def float_value(request, name):
    string_value = request.GET.get(name)
    if string_value is None:
        raise ParameterMissing(name)
    return float(string_value)


def optional_float_value(request, name, default_value):
    string_value = request.GET.get(name)
    if string_value is None:
        return default_value
    return float(string_value)


def sin_cos(angle):
    rad = angle / 180.0 * math.pi
    return math.sin(rad), math.cos(rad)


def hx_hy(stack, reach, ht_angle, spacers, stem_length, stem_angle):
    if ht_angle < 65 or ht_angle > 89:
        ht_angle = 73.0

    sin_hta, cos_hta = sin_cos(ht_angle)
    sin_stem_angle, cos_stem_angle = sin_cos(90.0 - ht_angle + stem_angle)
    sp_x = -(spacers + 20.0) * cos_hta
    sp_y = (spacers * sin_hta) + 20.0
    st_x = stem_length * cos_stem_angle
    st_y = stem_length * sin_stem_angle
    ret = HXHY()
    ret.stretch = sp_x + st_x
    ret.rise = sp_y + st_y
    ret.hx = round(reach + ret.stretch)
    ret.hy = round(stack + ret.rise)
    return ret


def stack_reach(frame_size: FrameSize, spacers: float, stem_length: float, stem_angle: float):
    return hx_hy(frame_size.stack, frame_size.reach, frame_size.headTubeAngle, spacers, stem_length, stem_angle)


class HXHY:
    def __init__(self):
        self.hx = 0
        self.hy = 0.0
        self.stretch = 0.0
        self.rise = 0.0


class Candidate:
    def __init__(self, frame_size, calc, hxhy):
        self.frame_size = frame_size
        self.spacers = calc.spacers
        self.stem_angle = calc.stem_angle
        self.stem_length = calc.stem_length
        self.stretch = hxhy.stretch
        self.rise = hxhy.rise
        self.hx = hxhy.hx
        self.hy = hxhy.hy
        self.distance = math.hypot(calc.hx - hxhy.hx, calc.hy - hxhy.hy)

    def frame(self):
        return self.frame_size.frame

    def brand(self):
        return self.frame_size.frame.brand

    @staticmethod
    def best(c1, c2):
        return c1 \
            if (c1.distance < c2.distance) or (c1.distance == c2.distance and c1.stem_angle < c2.stem_angle) \
            else c2

    def to_dict(self):
        return {
            "frame_size": self.frame_size.name,
            "frame_size_id": self.frame_size.id,
            "frame": self.frame().name,
            "frame_id": self.frame().id,
            "year_from": self.frame().yearFrom,
            "brand": self.frame().brand.name,
            "brand_id": self.frame().brand.id,
            "spacers": self.spacers,
            "stem_angle": self.stem_angle,
            "stem_length": self.stem_length,
            "stretch": self.stretch,
            "rise": self.rise,
            "hx": self.hx,
            "hy": self.hy,
            "distance": self.distance,
        }


class FitCalculation:
    def __init__(self,
                 hx, hy,
                 max_spacers=0.0,
                 min_stem_length=0.0,
                 max_stem_length=0.0,
                 frame=None,
                 frame_size=None):
        self.frame = frame
        self.frame_size = frame_size
        self.hx = hx
        self.hy = hy
        self._stem_angles = []
        self.stem_angle = 0.0
        self._min_stem_length = min_stem_length
        self._max_stem_length = max_stem_length
        self.stem_length = 0.0
        self._max_spacers = max_spacers
        self.spacers = 0.0
        self.all_or_best = AllResults if frame_size is None else OnlyBest
        self.threshold_x = 0.0
        self.threshold_y = 0.0

    def stem_angles(self):
        if self._stem_angles:
            return self._stem_angles
        else:
            return stem_angles

    def max_spacers(self):
        return self._max_spacers if self._max_spacers > 0 else 50

    def min_stem_length(self):
        return self._min_stem_length if self._min_stem_length > 60 else 60

    def max_stem_length(self):
        return self._max_stem_length if self._max_stem_length > 60 else 130

    def allow(self, calculated_hx, calculated_hy):
        threshold_x = self.threshold_x if self.threshold_x > 0.0 else 5.0
        threshold_y = self.threshold_y if self.threshold_y > 0.0 else 10.0
        allowed = abs(self.hx - calculated_hx) < threshold_x and abs(self.hy - calculated_hy) < threshold_y
        return allowed

    def no_threshold(self):
        self.threshold_x = 1000
        self.threshold_y = 1000

    def calculate(self):
        if self.frame_size:
            candidates = self.calculate_for_frame_size()
        elif self.frame:
            candidates = self.calculate_for_frame()
        else:
            candidates = self.calculate_for_all()

        if not candidates:
            return []

        if self.all_or_best == OnlyBest:
            best_candidate = self.find_best_candidate(candidates)
            logger.info("Overall best candidate: %s %s stem %0.0fmm %0.0f*, %0.0fmm spacers",
                        best_candidate.frame_size.frame.name,
                        best_candidate.frame_size.name,
                        best_candidate.stem_length, candidates[0].stem_angle, candidates[0].spacers)
            return [best_candidate]
        else:
            logger.info("Results for Stack %0.0f Reach %0.0f", self.hy, self.hx)
            for c in candidates:
                logger.info("%s %s stem %0.0fmm %0.0f*, %0.0fmm  --> %f %f",
                            c.frame_size.frame.name, c.frame_size.name,
                            c.stem_length, c.stem_angle, c.spacers, c.hx, c.hy)
            return candidates

    @staticmethod
    def find_best_candidate(candidates):
        if not candidates:
            return None

        best_candidate: Candidate = None
        distance: float = 0.0
        angle: float = 0.0
        for c in candidates:
            if not best_candidate or c.distance < distance or (c.distance == distance and c.stem_angle < angle):
                best_candidate = c
                distance = c.distance
                angle = c.stem_angle
        return best_candidate

    def calculate_for_all(self):
        candidates: [Candidate] = []
        frames: {int: Candidate} = {}
        for self.frame_size in FrameSize.objects.all():
            candidates_for_frame_size: [Candidate] = self.calculate_for_frame_size()
            if candidates_for_frame_size:
                best_candidate = self.find_best_candidate(candidates_for_frame_size)
                frame_id = best_candidate.frame_size.frame.id
                if frames.get(frame_id) is None:
                    frames[frame_id] = best_candidate
                else:
                    frames[frame_id] = Candidate.best(frames[frame_id], best_candidate)
        candidates.extend(frames.values())
        return candidates

    def calculate_for_frame(self):
        candidates: [Candidate] = []
        for self.frame_size in FrameSize.objects.filter(frame=self.frame):
            c: [Candidate] = self.calculate_for_frame_size()
            candidates.extend(c)
        logger.info("%s has %d candidates", self.frame.name, len(candidates))
        return candidates

    def calculate_for_frame_size(self):
        candidates: [Candidate] = []
        for self.stem_angle in self.stem_angles():
            self.spacers = 5.0
            while self.spacers < self.max_spacers() + 1.0:
                self.stem_length = self.min_stem_length()
                while self.stem_length <= self.max_stem_length():
                    hxhy = self.stack_reach()
                    if hxhy:
                        candidates.append(Candidate(self.frame_size, self, hxhy))
                    # logger.info("%s %s %f mm %f mm %f*: %f %f", self.frame_size.frame.id.name, self.frame_size.name,
                    #             self.spacers, self.stem_length, self.stem_angle, hxhy.hx, hxhy.hy)
                    self.stem_length += 10
                self.spacers += 2.5
        logger.info("%s %s has %d candidates", self.frame_size.frame.name, self.frame_size.name, len(candidates))
        return candidates

    def stack_reach(self):
        hxhy = stack_reach(self.frame_size, self.spacers, self.stem_length, self.stem_angle)
        return hxhy if self.allow(hxhy.hx, hxhy.hy) else None


def calculate(request):
    logger.info("%s /calculate: %s?%s", request.method, request.path, request.META["QUERY_STRING"])
    try:
        frame_size_id = optional_int_value(request, "size", -1)
        if frame_size_id >= 0:
            frame_size = FrameSize.objects.get(pk=frame_size_id)
            frame = None
        else:
            frame_size = None
            frame_id = optional_int_value(request, "frame", -1)
            frame = Frame.objects.get(pk=frame_id) if frame_id >= 0 else None
        calc = FitCalculation(
            float_value(request, "hx"),
            float_value(request, "hy"),
            optional_float_value(request, "MaxSpacers", 0.0),
            optional_float_value(request, "MinStemLength", 0.0),
            optional_float_value(request, "MaxStemLength", 0.0),
            frame,
            frame_size
        )
        response = [candidate.to_dict() for candidate in calc.calculate()]
        logger.info("%s /calculate: %s?%s: %d candidates",
                    request.method, request.path,
                    request.META["QUERY_STRING"], len(response))
        return JsonResponse(response, safe=False)
    except Exception as e:
        logger.info("%s /calculate: %s?%s", request.method, request.path, request.META["QUERY_STRING"], exc_info=e)
        return HttpResponseServerError(str(e))


def calculate_stack_reach(request):
    logger.info("%s /stackreach: %s?%s", request.method, request.path, request.META["QUERY_STRING"])
    try:
        size_id = float_value(request, "size")
        frame_size = FrameSize.objects.get(pk=size_id)
        spacers = float_value(request, "spacers")
        stem_length = float_value(request, "stemlength")
        stem_angle = float_value(request, "stemangle")
        ret = stack_reach(frame_size, spacers, stem_length, stem_angle)
        logger.info("%s /stackreach: %s?%s: hx %0.1f hy %0.1f", request.method, request.path,
                    request.META["QUERY_STRING"], ret.hx, ret.hy)
        return JsonResponse({"hx": ret.hx, "hy": ret.hy})
    except Exception as e:
        logger.error("%s /stackreach: %s?%s", request.method, request.path, request.META["QUERY_STRING"], exc_info=e)
        return HttpResponseServerError(str(e))
