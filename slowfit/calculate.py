import logging
import math

from django.http import HttpResponseServerError, HttpRequest, JsonResponse

from .models.bikes import Brand, Frame, FrameSize

logger = logging.getLogger(__name__)

stem_angles = [-17, -6, 6, 17]

# stem_lengths = [ 70, 80, 90, 95, 100, 105, 110, 120, 130, 140 ]
stem_lengths = [70, 80, 90, 95, 100, 105, 110, 120, 130]


class ParameterMissing(Exception):
    def __init__(self, param):
        self.param = param

    def __str__(self):
        return f"Parameter:self.param missing"


def int_value(request, name):
    string_value = request.POST.get(name, request.GET.get(name))
    if string_value is None:
        raise ParameterMissing(name)
    return int(string_value)


def optional_int_value(request, name, default_value=None):
    string_value = request.POST.get(name, request.GET.get(name))
    if string_value is None:
        return default_value
    return int(string_value)


def float_value(request, name):
    string_value = request.POST.get(name, request.GET.get(name))
    if string_value is None:
        raise ParameterMissing(name)
    return float(string_value)


def optional_float_value(request, name, default_value=None):
    string_value = request.POST.get(name, request.GET.get(name))
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


def stack_reach(spacers: float, stem_length: float, stem_angle: float,
                frame_size: FrameSize = None, stack: float = None, reach: float = None):
    if frame_size is not None:
        stack = frame_size.stack
        reach = frame_size.reach
    return hx_hy(stack, reach,
                 frame_size.headTubeAngle if frame_size else 73.0, spacers, stem_length, stem_angle)


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

    def __str__(self):
        if self.frame_size:
            return str(self.frame_size)
        else:
            return f"Stack XX Reach XX"

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
        ret = {
            "frame_size": "<none>",
            "frame_size_id": -1,
            "frame": "<none>",
            "frame_id": -1,
            "year_from": 2010,
            "brand": "<none>",
            "brand_id": -1,
            "spacers": self.spacers,
            "stem_angle": self.stem_angle,
            "stem_length": self.stem_length,
            "stretch": self.stretch,
            "rise": self.rise,
            "hx": self.hx,
            "hy": self.hy,
            "distance": self.distance,
        }
        if self.frame_size:
            ret.update({
                "frame_size": self.frame_size.name,
                "frame_size_id": self.frame_size.id,
                "frame": self.frame().name,
                "frame_id": self.frame().id,
                "year_from": self.frame().yearFrom,
                "brand": self.frame().brand.name,
                "brand_id": self.frame().brand.id,
            })
        return ret


class FitCalculation:
    AllResults = "ALL"
    OnlyBest = "ONLYBEST"

    def __init__(self,
                 hx, hy,
                 max_spacers=0.0,
                 min_stem_length=0.0,
                 max_stem_length=0.0,
                 frame=None,
                 frame_size=None,
                 stack=None,
                 reach=None,
                 all_or_best=None):
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
        self.all_or_best = all_or_best or (self.AllResults if frame_size is None else self.OnlyBest)
        self.threshold_x = 0.0
        self.threshold_y = 0.0
        self.stack = stack
        self.reach = reach

    def __str__(self):
        if self.frame_size:
            return str(self.frame_size)
        elif self.frame:
            return str(self.frame)
        else:
            return f"Stack {self.stack}mm Reach {self.reach}mm"

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
        elif self.stack is not None and self.stack > 0:
            candidates = self.calculate_for_frame_size()
        else:
            candidates = self.calculate_for_all()

        if not candidates:
            return []

        if self.all_or_best == self.OnlyBest:
            best_candidate = self.find_best_candidate(candidates)
            logger.info("Overall best candidate: %s stem %0.0fmm %0.0f*, %0.0fmm spacers",
                        best_candidate, best_candidate.stem_length, candidates[0].stem_angle, candidates[0].spacers)
            return [best_candidate]
        else:
            logger.info("Results for Stack %0.0f Reach %0.0f", self.hy, self.hx)
            for c in candidates:
                logger.info("%s stem %0.0fmm %0.0f*, %0.0fmm  --> %f %f",
                            self,
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
        logger.info("%s has %d candidates", self, len(candidates))
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
                        candidate = Candidate(self.frame_size, self, hxhy)
                        candidates.append(candidate)
                        # logger.info("%s %f mm %f mm %f*: %f %f (%f)", self, self.spacers, self.stem_length, self.stem_angle,
                        #             hxhy.hx, hxhy.hy, candidate.distance)
                    self.stem_length += 10
                self.spacers += 2.5
        logger.info("%s has %d candidates", self, len(candidates))
        return candidates

    def stack_reach(self):
        hxhy = stack_reach(self.spacers, self.stem_length, self.stem_angle,
                           frame_size=self.frame_size, stack=self.stack, reach=self.reach)
        return hxhy if self.allow(hxhy.hx, hxhy.hy) else None


def calculate(request: HttpRequest):
    logger.info("%s /calculate: %s?%s", request.method, request.path, request.META["QUERY_STRING"])
    try:
        frame = None
        frame_size = None
        frame_size_id = optional_int_value(request, "size")
        frame_id = optional_int_value(request, "frame")
        stack = optional_int_value(request, "stack")
        reach = optional_int_value(request, "reach")
        if frame_size_id is not None:
            frame_size = FrameSize.objects.get(pk=frame_size_id)
            frame = None
        elif frame_id is not None:
            frame_size = None
            frame = Frame.objects.get(pk=frame_id) if frame_id >= 0 else None
        all_or_best = request.POST.get("all_or_best", request.GET.get("all_or_best"))
        calc = FitCalculation(
            float_value(request, "hx"),
            float_value(request, "hy"),
            max_spacers=optional_float_value(request, "MaxSpacers", 0.0),
            min_stem_length=optional_float_value(request, "MinStemLength", 0.0),
            max_stem_length=optional_float_value(request, "MaxStemLength", 0.0),
            frame=frame,
            frame_size=frame_size,
            stack=stack,
            reach=reach,
            all_or_best=all_or_best
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
