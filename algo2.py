import numpy as np

class AlignmentScoring:
	def __init__(self, match, mismatch, gap_start, gap):
		self.match = match
		self.mismatch = mismatch
		self.gap_start = gap_start
		self.gap = gap

class FOGSAABranch:
	def __init__(self, m, x, y):
		self.m = m
		self.x = x
		self.y = y

XY = 0x1
xY = 0x2
Xy = 0x3

def print_alignment(X, Y, ox, oy, alignments):
	Xa = X[ox:]
	Ya = Y[oy:]

	xx = ox
	yy = oy

	while xx != 0 and yy != 0:
		if alignments[xx][yy] == xY:
			yy -= 1
			Xa = "-" + Xa
			Ya = Y[yy] + Ya
		elif alignments[xx][yy] == Xy:
			xx -= 1
			Xa = X[xx] + Xa
			Ya = "-" + Ya
		else:
			xx -= 1
			yy -= 1
			Xa = X[xx] + Xa
			Ya = Y[yy] + Ya

	if xx != 0:
		Xa = X[:xx] + Xa
		Ya = "-" * xx + Ya
	elif yy != 0:
		Ya = Y[:yy] + Ya
		Xa = "-" * yy + Xa

	r = len(Xa) - len(Ya)

	if r < 0:
		Xa = Xa + "-" * (-r)
	else:
		Ya = Ya + "-" * r

	return Xa, Ya


def fogsaa_algo(X, Y, s):
	num_comp = 0
	g0 = len(X) - len(Y)
	gM = 0 if g0 == 0 else s.gap_start

	if g0 < 0:
		gM += -g0 * s.gap
		m0 = len(X)
	else:
		gM = g0 * s.gap
		m0 = len(Y)

	gm = gM + m0 * s.mismatch
	gM += m0 * s.match

	t = (len(X) + 1, len(Y) + 1)
	alignments = np.zeros(t, dtype=np.uint8)
	scores = np.empty(t, dtype=np.int_)
	scores.fill(gm)
	scores[0][0] = 0

	Mi = mi = gM - gm
	queue = [[] for _ in range(Mi + 1)]
	queue[Mi] = [FOGSAABranch(0, 0, 0)]

	def enqueue(M, m, x, y, alignment):
		nonlocal Mi
		nonlocal mi

		if alignment & 1 != 0:
			x = -x

		if alignment & 2 != 0:
			y = -y

		branch = FOGSAABranch(m, x, y)

		i = M - gm

		if i > Mi:
			Mi = i

		if i < mi or mi == -1:
			mi = i

		j = 0

		while j < len(queue[i]) and queue[i][j].m <= m:
			j += 1

		queue[i].insert(j, branch)

	def dequeue():
		nonlocal Mi
		nonlocal mi

		x = queue[Mi][-1].x
		y = queue[Mi][-1].y

		queue[Mi].pop()

		alignment = 0x0

		if x < 0:
			x = -x
			alignment |= 0x1

		if y < 0:
			y = -y
			alignment |= 0x2

		while not queue[Mi]:
			if Mi == mi:
				Mi = mi = -1
				break

			Mi -= 1

		return (x, y, alignment)

	ox = len(X)
	oy = len(Y)

	while Mi + gm > scores[ox, oy]:
		x, y, alignment = dequeue()

		while x < len(X) and y < len(Y):
			num_comp += 2
			positions = 0x0
			score = [scores[x][y] + (s.match if X[x] == Y[y] else s.mismatch),
				 scores[x][y] + s.gap + (0 if alignment == xY else s.gap_start),
				 scores[x][y] + s.gap + (0 if alignment == Xy else s.gap_start)]
			Mm = [(0, 0) for _ in range(3)]

			if score[XY-1] > scores[x + 1][y + 1]:
				num_comp += 1
				scores[x + 1][y + 1] = M = score[XY-1]
				rx = len(X) - 1 - x
				ry = len(Y) - 1 - y
				g = rx - ry
				r = ry

				if g != 0:
					M += s.gap_start

					if g < 0:
						g = -g
						r = rx

				M += g * s.gap
				m = M + r * s.mismatch
				M += r * s.match

				if M > scores[ox][oy]:
					Mm[XY-1] = (M, m)
					positions = XY

			if score[xY-1] > scores[x][y + 1]:
				num_comp += 1
				scores[x][y + 1] = M = score[xY-1]
				rx = len(X) - x
				ry = len(Y) - 1 - y
				g = ry - rx
				r = rx

				if g < 0:
					g = -g
					r = ry
					M += s.gap_start

				M += g * s.gap
				m = M + r * s.mismatch
				M += r * s.match

				if M > scores[ox][oy]:
					Mm[xY-1] = (M, m)

					if positions == 0x0 or Mm[xY-1] > Mm[XY-1]:
						positions <<= 2
						positions |= xY
					else:
						positions |= xY << 2

			if score[Xy-1] > scores[x + 1][y]:
				num_comp += 1
				scores[x + 1][y] = M = score[Xy-1]
				rx = len(X) - 1 - x
				ry = len(Y) - y
				g = rx - ry
				r = ry

				if g < 0:
					g = -g
					r = rx
					M += s.gap_start

				M += g * s.gap
				m = M + r * s.mismatch
				M += r * s.match

				if M > scores[ox][oy]:
					Mm[Xy-1] = (M, m)

					t = positions >> 2

					if t == 0 or Mm[Xy-1] > Mm[t-1]:
						u = positions & 0b11

						if u == 0 or Mm[Xy-1] > Mm[u-1]:
							positions <<= 2
							positions |= Xy
						else:
							positions = u
							t = t << 4 | Xy << 2
							positions |= t
					else:
						positions |= Xy << 4

			alignment = positions & 0b11

			if alignment == 0x0:
				num_comp += 1
				break

			a = (positions & 0b1100) >> 2

			if a != 0 and Mm[a-1][0] > Mm[alignment-1][1]:
				num_comp += 1
				enqueue(Mm[a-1][0], Mm[a-1][1],
					(x if a == xY else (x + 1)),
					(y if a == Xy else (y + 1)), a)

				b = positions >> 4

				if b != 0 and Mm[b-1][0] > Mm[a-1][1]:
					enqueue(Mm[b-1][0], Mm[b-1][1],
						(x if b == xY else (x + 1)),
						(y if b == Xy else (y + 1)), b)

			x = x if alignment == xY else (x + 1)
			y = y if alignment == Xy else (y + 1)
			alignments[x][y] = alignment
		else:
			ox = x
			oy = y

	x_aligned, y_aligned = print_alignment(X, Y, ox, oy, alignments)
	return x_aligned, y_aligned, num_comp


def FOGSAA(seq1, seq2, debug, gap=0, match=1, mismatch=-1):
	return fogsaa_algo(seq1, seq2, AlignmentScoring(match, mismatch, 0, gap))

if __name__=='__main__':
	x, y, num = FOGSAA("EDIT", "DISTANCE", False, gap=-1, match=1, mismatch=-1)
	print(x)
	print(y)
	print(num)











