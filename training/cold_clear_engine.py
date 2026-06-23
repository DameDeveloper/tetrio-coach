"""
Cold Clear 테트리스 AI 엔진 래퍼.

Cold Clear DLL을 로드하여 주어진 보드 상태 + 피스 큐에 대한 최적 배치를 계산한다.
DLL이 없으면 내장 휴리스틱 폴백을 사용한다.
"""

import ctypes
import enum
import time
from pathlib import Path

_LIB = None
_AVAILABLE = False


class Piece(enum.IntEnum):
    I = 0; O = 1; T = 2; L = 3; J = 4; S = 5; Z = 6

PIECE_MAP = {'i':Piece.I,'o':Piece.O,'t':Piece.T,'l':Piece.L,'j':Piece.J,'s':Piece.S,'z':Piece.Z}

class TspinStatus(enum.IntEnum):
    NONE = 0; MINI = 1; FULL = 2

class Movement(enum.IntEnum):
    LEFT = 0; RIGHT = 1; CW = 2; CCW = 3; DROP = 4

class PollStatus(enum.IntEnum):
    MOVE_PROVIDED = 0; WAITING = 1; DEAD = 2


class _CCOptions(ctypes.Structure):
    _fields_ = [
        ("mode", ctypes.c_int), ("spawn_rule", ctypes.c_int),
        ("pcloop", ctypes.c_int), ("min_nodes", ctypes.c_uint32),
        ("max_nodes", ctypes.c_uint32), ("threads", ctypes.c_uint32),
        ("use_hold", ctypes.c_bool), ("speculate", ctypes.c_bool),
    ]

class _CCWeights(ctypes.Structure):
    _fields_ = [
        ("back_to_back", ctypes.c_int32), ("bumpiness", ctypes.c_int32),
        ("bumpiness_sq", ctypes.c_int32), ("row_transitions", ctypes.c_int32),
        ("height", ctypes.c_int32), ("top_half", ctypes.c_int32),
        ("top_quarter", ctypes.c_int32), ("jeopardy", ctypes.c_int32),
        ("cavity_cells", ctypes.c_int32), ("cavity_cells_sq", ctypes.c_int32),
        ("overhang_cells", ctypes.c_int32), ("overhang_cells_sq", ctypes.c_int32),
        ("covered_cells", ctypes.c_int32), ("covered_cells_sq", ctypes.c_int32),
        ("tslot", ctypes.c_int32 * 4), ("well_depth", ctypes.c_int32),
        ("max_well_depth", ctypes.c_int32), ("well_column", ctypes.c_int32 * 10),
        ("b2b_clear", ctypes.c_int32), ("clear1", ctypes.c_int32),
        ("clear2", ctypes.c_int32), ("clear3", ctypes.c_int32),
        ("clear4", ctypes.c_int32), ("tspin1", ctypes.c_int32),
        ("tspin2", ctypes.c_int32), ("tspin3", ctypes.c_int32),
        ("mini_tspin1", ctypes.c_int32), ("mini_tspin2", ctypes.c_int32),
        ("perfect_clear", ctypes.c_int32), ("combo_garbage", ctypes.c_int32),
        ("move_time", ctypes.c_int32), ("wasted_t", ctypes.c_int32),
        ("use_bag", ctypes.c_bool), ("timed_jeopardy", ctypes.c_bool),
        ("stack_pc_damage", ctypes.c_bool),
    ]

class _CCMove(ctypes.Structure):
    _fields_ = [
        ("hold", ctypes.c_bool),
        ("expected_x", ctypes.c_uint8 * 4), ("expected_y", ctypes.c_uint8 * 4),
        ("movement_count", ctypes.c_uint8), ("movements", ctypes.c_int * 32),
        ("nodes", ctypes.c_uint32), ("depth", ctypes.c_uint32),
        ("original_rank", ctypes.c_uint32),
    ]


def init(dll_path: str | None = None) -> bool:
    """Cold Clear DLL을 로드. 성공 시 True."""
    global _LIB, _AVAILABLE
    if _AVAILABLE:
        return True

    if dll_path is None:
        from _paths import get_base_dir
        base = get_base_dir()
        candidates = [
            base / 'lib' / 'cold_clear.dll',
            Path(__file__).parent.parent / 'lib' / 'cold_clear.dll',
            Path(__file__).parent / 'cold_clear.dll',
            Path('cold_clear.dll'),
        ]
        for p in candidates:
            if p.exists():
                dll_path = str(p)
                break

    if not dll_path or not Path(dll_path).exists():
        return False

    try:
        _LIB = ctypes.cdll.LoadLibrary(dll_path)
        _LIB.cc_launch_async.restype = ctypes.c_void_p
        _LIB.cc_destroy_async.restype = None
        _LIB.cc_reset_async.restype = None
        _LIB.cc_add_next_piece_async.restype = None
        _LIB.cc_request_next_move.restype = None
        _LIB.cc_poll_next_move.restype = ctypes.c_int
        _LIB.cc_default_options.restype = None
        _LIB.cc_default_weights.restype = None
        _AVAILABLE = True
        return True
    except Exception:
        _AVAILABLE = False
        return False


def is_available() -> bool:
    return _AVAILABLE


class ColdClearBot:
    """Cold Clear 봇 인스턴스. with문으로 사용."""

    def __init__(self):
        if not globals()['_AVAILABLE']:
            raise RuntimeError("Cold Clear DLL이 로드되지 않았습니다. init()을 먼저 호출하세요.")
        lib = globals()['_LIB']
        opts = ctypes.create_string_buffer(128)
        lib.cc_default_options(opts)
        weights = ctypes.create_string_buffer(256)
        lib.cc_default_weights(weights)
        self._handle = ctypes.cast(lib.cc_launch_async(opts, weights), ctypes.c_void_p)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        if self._handle is not None:
            self._lib().cc_destroy_async(self._handle)
            self._handle = None

    def _lib(self):
        return globals()['_LIB']

    def add_piece(self, piece: str | int | Piece):
        if isinstance(piece, str):
            piece = PIECE_MAP.get(piece.lower(), 0)
        self._lib().cc_add_next_piece_async(self._handle, ctypes.c_int(int(piece)))

    def reset_board(self, field: list[list[bool]], b2b: bool = False, combo: int = 0):
        raw = (ctypes.c_bool * 400)()
        for y, row in enumerate(field):
            for x, cell in enumerate(row):
                raw[x + y * 10] = bool(cell)
        self._lib().cc_reset_async(self._handle, ctypes.byref(raw), ctypes.c_bool(b2b), ctypes.c_uint32(combo))

    def request_move(self, incoming_garbage: int = 0):
        self._lib().cc_request_next_move(self._handle, ctypes.c_uint32(incoming_garbage))

    def poll_move(self, timeout: float = 2.0) -> dict | None:
        lib = self._lib()
        buf = ctypes.create_string_buffer(256)
        deadline = time.time() + timeout
        while time.time() < deadline:
            status = lib.cc_poll_next_move(self._handle, buf, None, None)
            if status == 0:
                raw = bytes(buf)
                hold = bool(raw[0])
                cells = [(raw[1+i], raw[5+i]) for i in range(4)]
                mc = raw[9]
                movements = []
                base = 12
                for i in range(min(mc, 32)):
                    v = int.from_bytes(raw[base+i*4:base+i*4+4], 'little', signed=True)
                    if 0 <= v <= 4:
                        movements.append(Movement(v).name)
                nodes = int.from_bytes(raw[base+32*4:base+32*4+4], 'little')
                depth = int.from_bytes(raw[base+33*4:base+33*4+4], 'little')
                return {
                    'hold': hold, 'cells': cells,
                    'movements': movements, 'nodes': nodes, 'depth': depth,
                }
            if status == 2:
                return None
            time.sleep(0.02)
        return None

    def get_best_move(self, pieces: list[str], incoming: int = 0, timeout: float = 2.0) -> dict | None:
        """피스 큐를 주고 최적 배치를 받는 편의 메서드."""
        for p in pieces:
            self.add_piece(p)
        time.sleep(0.3)
        self.request_move(incoming)
        return self.poll_move(timeout)


def evaluate_placement(queue: list[str], timeout: float = 1.0) -> dict | None:
    """빈 보드에서 주어진 큐의 첫 번째 피스에 대한 최적 배치를 반환."""
    if not _AVAILABLE:
        return None
    try:
        with ColdClearBot() as bot:
            return bot.get_best_move(queue, timeout=timeout)
    except Exception:
        return None


def evaluate_sequence(pieces: list[str], count: int = 0, timeout_per_move: float = 0.5) -> list[dict]:
    """피스 시퀀스의 각 배치에 대한 최적 수를 연속으로 계산."""
    if not _AVAILABLE:
        return []
    if count <= 0:
        count = len(pieces)

    results = []
    try:
        with ColdClearBot() as bot:
            for p in pieces[:count + 5]:
                bot.add_piece(p)

            for i in range(min(count, len(pieces))):
                bot.request_move(0)
                move = bot.poll_move(timeout_per_move)
                if move is None:
                    break
                move['piece_index'] = i
                move['piece'] = pieces[i] if i < len(pieces) else '?'
                results.append(move)
    except Exception:
        pass
    return results


# ── 내장 휴리스틱 폴백 (Cold Clear 없을 때) ──

def _heuristic_score(heights: list[int], holes: int, bumpiness: int) -> float:
    max_h = max(heights) if heights else 0
    agg_h = sum(heights)
    return -(0.51 * agg_h + 0.36 * holes * 10 + 0.18 * bumpiness + 0.1 * max_h)


def heuristic_evaluate(heights: list[int], holes: int, bumpiness: int) -> dict:
    """Cold Clear 없을 때 사용하는 간단한 보드 평가."""
    score = _heuristic_score(heights, holes, bumpiness)
    max_h = max(heights) if heights else 0

    risk = 'low'
    if max_h >= 15 or holes >= 5:
        risk = 'high'
    elif max_h >= 10 or holes >= 3:
        risk = 'medium'

    return {
        'score': round(score, 2),
        'risk': risk,
        'max_height': max_h,
        'aggregate_height': sum(heights),
        'holes': holes,
        'bumpiness': bumpiness,
    }
