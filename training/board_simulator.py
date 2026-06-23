"""
Phase 2: ttrm 리플레이 → 보드 상태 시뮬레이터 (DAS/ARR 지원)

ttrm 파일의 keydown/keyup 이벤트 + DAS/ARR 핸들링을 정확히 재현하여
매 배치마다의 10x40 보드 상태를 출력한다.

좌표계: TETR.IO와 동일 — y=0이 상단, y=39가 바닥.
"""

import json
from pathlib import Path

PIECES = {
    'i': {0:[(0,1),(1,1),(2,1),(3,1)], 1:[(2,0),(2,1),(2,2),(2,3)], 2:[(0,2),(1,2),(2,2),(3,2)], 3:[(1,0),(1,1),(1,2),(1,3)]},
    'o': {0:[(0,0),(1,0),(0,1),(1,1)], 1:[(0,0),(1,0),(0,1),(1,1)], 2:[(0,0),(1,0),(0,1),(1,1)], 3:[(0,0),(1,0),(0,1),(1,1)]},
    't': {0:[(0,0),(1,0),(2,0),(1,1)], 1:[(1,0),(1,1),(2,1),(1,2)], 2:[(1,0),(0,1),(1,1),(2,1)], 3:[(1,0),(0,1),(1,1),(1,2)]},
    's': {0:[(1,0),(2,0),(0,1),(1,1)], 1:[(1,0),(1,1),(2,1),(2,2)], 2:[(1,1),(2,1),(0,2),(1,2)], 3:[(0,0),(0,1),(1,1),(1,2)]},
    'z': {0:[(0,0),(1,0),(1,1),(2,1)], 1:[(2,0),(1,1),(2,1),(1,2)], 2:[(0,1),(1,1),(1,2),(2,2)], 3:[(1,0),(0,1),(1,1),(0,2)]},
    'l': {0:[(0,0),(1,0),(2,0),(0,1)], 1:[(1,0),(2,0),(2,1),(2,2)], 2:[(2,1),(0,2),(1,2),(2,2)], 3:[(0,0),(0,1),(0,2),(1,2)]},
    'j': {0:[(0,0),(1,0),(2,0),(2,1)], 1:[(2,0),(2,1),(1,2),(2,2)], 2:[(0,1),(0,2),(1,2),(2,2)], 3:[(0,0),(1,0),(0,1),(0,2)]},
}
KICK_NORMAL = {
    (0,1):[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)], (1,0):[(0,0),(1,0),(1,1),(0,-2),(1,-2)],
    (1,2):[(0,0),(1,0),(1,-1),(0,2),(1,2)], (2,1):[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
    (2,3):[(0,0),(1,0),(1,-1),(0,2),(1,2)], (3,2):[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
    (3,0):[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)], (0,3):[(0,0),(1,0),(1,1),(0,-2),(1,-2)],
}
KICK_I = {
    (0,1):[(0,0),(-2,0),(1,0),(-2,1),(1,-2)], (1,0):[(0,0),(2,0),(-1,0),(2,-1),(-1,2)],
    (1,2):[(0,0),(-1,0),(2,0),(-1,-2),(2,1)], (2,1):[(0,0),(1,0),(-2,0),(1,2),(-2,-1)],
    (2,3):[(0,0),(2,0),(-1,0),(2,-1),(-1,2)], (3,2):[(0,0),(-2,0),(1,0),(-2,1),(1,-2)],
    (3,0):[(0,0),(1,0),(-2,0),(1,2),(-2,-1)], (0,3):[(0,0),(-1,0),(2,0),(-1,-2),(2,1)],
}
WIDTH, HEIGHT = 10, 40
SPAWN = {'i':(3,0),'o':(4,0),'t':(3,0),'s':(3,0),'z':(3,0),'l':(3,0),'j':(3,0)}


def _cells(piece: str, r: int) -> list[tuple[int,int]]:
    return PIECES[piece][r % 4]


class Board:
    def __init__(self):
        self.grid = [[None]*WIDTH for _ in range(HEIGHT)]
        self.combo = -1
        self.b2b = -1

    def occupied(self, x: int, y: int) -> bool:
        if x < 0 or x >= WIDTH or y >= HEIGHT: return True
        if y < 0: return False
        return self.grid[y][x] is not None

    def fits(self, pc: str, x: int, y: int, r: int) -> bool:
        return all(not self.occupied(x+dx, y+dy) for dx,dy in _cells(pc, r))

    def place(self, pc: str, x: int, y: int, r: int) -> dict:
        for dx, dy in _cells(pc, r):
            bx, by = x+dx, y+dy
            if 0 <= bx < WIDTH and 0 <= by < HEIGHT:
                self.grid[by][bx] = pc
        cleared = self._clear()
        tspin = self._tspin_check(pc, x, y, r)
        if cleared > 0:
            self.combo += 1
            if tspin or cleared >= 4: self.b2b += 1
            else: self.b2b = -1
        else:
            self.combo = -1
        ac = all(self.grid[HEIGHT-1][c] is None for c in range(WIDTH))
        return {'lines': cleared, 'tspin': tspin, 'combo': max(self.combo,0), 'b2b': max(self.b2b,0), 'allclear': ac}

    def _clear(self) -> int:
        new = [r for r in self.grid if not all(c is not None for c in r)]
        n = HEIGHT - len(new)
        self.grid = [[None]*WIDTH for _ in range(n)] + new
        return n

    def _tspin_check(self, pc, x, y, r) -> bool:
        if pc != 't': return False
        cx, cy = x+1, y+1
        return sum(1 for cx2,cy2 in [(cx-1,cy-1),(cx+1,cy-1),(cx-1,cy+1),(cx+1,cy+1)] if self.occupied(cx2,cy2)) >= 3

    def add_garbage(self, lines: int, hole_x: int):
        self.grid = self.grid[lines:] + [[(None if c==hole_x else 'g') for c in range(WIDTH)] for _ in range(lines)]

    def height_map(self) -> list[int]:
        h = []
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if self.grid[y][x] is not None:
                    h.append(HEIGHT-y); break
            else:
                h.append(0)
        return h

    def hole_count(self) -> int:
        holes = 0
        for x in range(WIDTH):
            found = False
            for y in range(HEIGHT):
                if self.grid[y][x] is not None: found = True
                elif found: holes += 1
        return holes

    def snapshot(self) -> list[list[str|None]]:
        top = HEIGHT
        for y in range(HEIGHT):
            if any(self.grid[y][x] is not None for x in range(WIDTH)):
                top = y; break
        return [r[:] for r in self.grid[max(0,top-2):]]

    def bumpiness(self) -> int:
        hm = self.height_map()
        return sum(abs(hm[i]-hm[i+1]) for i in range(len(hm)-1))

    def aggregate_height(self) -> int:
        return sum(self.height_map())


def _kick(board, pc, x, y, rf, rt):
    table = KICK_I if pc == 'i' else KICK_NORMAL
    for dx,dy in table.get((rf,rt),[(0,0)]):
        if board.fits(pc, x+dx, y+dy, rt): return (x+dx, y+dy, rt)
    return None


def _rng(seed):
    t = seed % (2**32)
    while True:
        t = (t + 0x6D2B79F5) % (2**32)
        r = t; r = ((r^(r>>15))*(r|1))%(2**32); r = (r^((r^(r>>7))*(r|61)))%(2**32); r = (r^(r>>14))%(2**32)
        yield r / (2**32)


def _gen_bag(rng):
    b = list('itoszlj')
    for i in range(len(b)-1, 0, -1):
        j = int(next(rng)*(i+1)); b[i],b[j] = b[j],b[i]
    return b


def simulate_round(events: list[dict], seed: int) -> list[dict]:
    board = Board()
    placements = []
    rng = _rng(seed)
    cur = None
    cx = cy = cr = 0
    hold = None
    hold_locked = False
    bag: list[str] = []
    last_kick_used = False

    # DAS/ARR state
    arr = 0.5
    das = 6.5
    left_held = False
    right_held = False
    left_das_timer = 0.0
    right_das_timer = 0.0
    last_frame = 0

    def _refill():
        while len(bag) < 14:
            bag.extend(_gen_bag(rng))

    def _spawn(pc):
        nonlocal cx, cy, cr, last_kick_used
        sx, sy = SPAWN.get(pc, (3,0))
        cx, cy, cr = sx, sy, 0
        last_kick_used = False

    def _move_left():
        nonlocal cx
        if board.fits(cur, cx-1, cy, cr): cx -= 1

    def _move_right():
        nonlocal cx
        if board.fits(cur, cx+1, cy, cr): cx += 1

    def _process_das(frame):
        nonlocal left_das_timer, right_das_timer
        if cur is None: return
        elapsed = frame - last_frame
        if elapsed <= 0: return

        if left_held and not right_held:
            left_das_timer += elapsed
            if left_das_timer >= das:
                if arr <= 0 or arr < 1:
                    while board.fits(cur, cx-1, cy, cr):
                        _move_left()
                else:
                    moves = int((left_das_timer - das) / arr)
                    for _ in range(moves):
                        _move_left()
        elif right_held and not left_held:
            right_das_timer += elapsed
            if right_das_timer >= das:
                if arr <= 0 or arr < 1:
                    while board.fits(cur, cx+1, cy, cr):
                        _move_right()
                else:
                    moves = int((right_das_timer - das) / arr)
                    for _ in range(moves):
                        _move_right()

    for ev in events:
        t = ev.get('type', '')

        if t == 'full':
            game = ev['data'].get('game', {})
            f = game.get('falling', {})
            cur = f.get('type')
            cx, cy, cr = f.get('x',0), f.get('y',0), f.get('r',0)
            bag.clear()
            bag.extend(game.get('bag', []))
            _refill()
            h = game.get('hold', {})
            if isinstance(h, dict):
                hold, hold_locked = h.get('piece'), h.get('locked', False)
            hdl = game.get('handling', {})
            if isinstance(hdl, dict):
                arr = hdl.get('arr', 0.5)
                das = hdl.get('das', 6.5)
            continue

        if t == 'ige':
            ige = ev.get('data',{}).get('data',{})
            if ige.get('type') == 'garbage':
                amt = ige.get('amt',0) or ige.get('lines',0)
                if amt > 0: board.add_garbage(amt, ige.get('x',0))
            continue

        if t not in ('keydown', 'keyup') or cur is None:
            continue

        frame = ev.get('frame', 0)
        subframe = ev.get('data',{}).get('subframe', 0)
        eff_frame = frame + subframe

        _process_das(eff_frame)
        last_frame = eff_frame

        if t == 'keyup':
            key = ev.get('data',{}).get('key','')
            if key == 'moveLeft': left_held = False; left_das_timer = 0
            elif key == 'moveRight': right_held = False; right_das_timer = 0
            continue

        key = ev.get('data',{}).get('key','')

        if key == 'moveLeft':
            left_held = True
            left_das_timer = 0
            _move_left()
        elif key == 'moveRight':
            right_held = True
            right_das_timer = 0
            _move_right()
        elif key == 'rotateCW':
            k = _kick(board, cur, cx, cy, cr, (cr+1)%4)
            if k:
                cx, cy, cr = k
                last_kick_used = (k[0] != cx or k[1] != cy)
        elif key == 'rotateCCW':
            k = _kick(board, cur, cx, cy, cr, (cr+3)%4)
            if k:
                cx, cy, cr = k
                last_kick_used = (k[0] != cx or k[1] != cy)
        elif key == 'rotate180':
            nr = (cr+2)%4
            if board.fits(cur, cx, cy, nr): cr = nr
        elif key == 'softDrop':
            while board.fits(cur, cx, cy+1, cr): cy += 1
        elif key == 'hardDrop':
            while board.fits(cur, cx, cy+1, cr): cy += 1
            res = board.place(cur, cx, cy, cr)
            placements.append({
                'i': len(placements), 'frame': frame,
                'piece': cur, 'x': cx, 'y': cy, 'r': cr,
                'hold': hold,
                'lines': res['lines'], 'tspin': res['tspin'],
                'combo': res['combo'], 'b2b': res['b2b'], 'allclear': res['allclear'],
                'heights': board.height_map(), 'holes': board.hole_count(),
                'bumpiness': board.bumpiness(),
                'queue': bag[:5],
            })
            _refill()
            cur = bag.pop(0)
            _spawn(cur)
            hold_locked = False
            left_held = right_held = False
            left_das_timer = right_das_timer = 0
        elif key == 'hold':
            if not hold_locked:
                if hold is None:
                    hold = cur; _refill(); cur = bag.pop(0)
                else:
                    hold, cur = cur, hold
                _spawn(cur)
                hold_locked = True
                left_held = right_held = False
                left_das_timer = right_das_timer = 0

    return placements


def simulate_ttrm(filepath: str) -> list[dict]:
    raw = json.loads(Path(filepath).read_text(encoding='utf-8'))
    rounds_raw = raw.get('replay',{}).get('rounds',[])
    results = []
    for rd_idx, scoreboard in enumerate(rounds_raw):
        if not isinstance(scoreboard, list): continue
        for entry in scoreboard:
            if not isinstance(entry, dict): continue
            er = entry.get('replay',{})
            if not isinstance(er, dict): continue
            evts = er.get('events',[])
            sd = er.get('options',{}).get('seed',0)
            if evts:
                pls = simulate_round(evts, sd)
                results.append({
                    'round': rd_idx+1, 'username': entry.get('username',''),
                    'seed': sd, 'placements': pls, 'total_pieces': len(pls),
                })
    return results


def extract_features(placements: list[dict]) -> dict:
    """배치 시퀀스에서 학습/평가용 특성 추출."""
    if not placements:
        return {}
    n = len(placements)
    lines = sum(p['lines'] for p in placements)
    tspins = sum(1 for p in placements if p['tspin'])
    quads = sum(1 for p in placements if p['lines'] >= 4)
    allclears = sum(1 for p in placements if p['allclear'])
    max_combo = max((p['combo'] for p in placements), default=0)
    max_b2b = max((p['b2b'] for p in placements), default=0)
    avg_height = sum(max(p['heights']) for p in placements) / n
    avg_holes = sum(p['holes'] for p in placements) / n
    avg_bump = sum(p['bumpiness'] for p in placements) / n

    # 오프닝 효율 (처음 10배치)
    opener = placements[:min(10, n)]
    opener_tspins = sum(1 for p in opener if p['tspin'])
    opener_lines = sum(p['lines'] for p in opener)

    # 수비력 (높은 보드에서의 클리어)
    high_board_clears = sum(1 for p in placements if max(p['heights']) >= 15 and p['lines'] > 0)

    return {
        'total_pieces': n,
        'total_lines': lines,
        'lines_per_piece': round(lines / n, 3),
        'total_tspins': tspins,
        'tspin_rate': round(tspins / n * 100, 2),
        'total_quads': quads,
        'total_allclears': allclears,
        'max_combo': max_combo,
        'max_b2b': max_b2b,
        'avg_max_height': round(avg_height, 1),
        'avg_holes': round(avg_holes, 1),
        'avg_bumpiness': round(avg_bump, 1),
        'opener_tspins': opener_tspins,
        'opener_lines': opener_lines,
        'high_board_clears': high_board_clears,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python board_simulator.py <ttrm_path>"); sys.exit(1)
    rounds = simulate_ttrm(sys.argv[1])
    print(f"시뮬레이션: {len(rounds)}개 엔트리")
    for rd in rounds:
        pls = rd['placements']
        f = extract_features(pls)
        print(f"  {rd['username']:15s} R{rd['round']}: {f.get('total_pieces',0):3d}pcs L={f.get('total_lines',0)} TS={f.get('total_tspins',0)} Q={f.get('total_quads',0)} Combo={f.get('max_combo',0)} B2B={f.get('max_b2b',0)}")
