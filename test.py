import Image
import math
import itertools

def gaussian(x, y, sigma):
	return (1 / (2*math.pi*sigma**2))*math.exp(-(x**2+y**2)/(2*sigma**2))

name = "stapler"

im = Image.open(name + ".png")
print im.format, im.size, im.mode
bw = im.convert("L")
bw.save(name + "_bw.png", "PNG")
bw_pix = bw.load()
width = bw.size[0]
height = bw.size[1]

sigma = 1
convolution = [ [0 for col in range(bw.size[1])] for row in range(bw.size[0])]
# Loop over every pixel in the image and apply the Gaussian filter
for (x,y) in itertools.product(range(bw.size[0]), range(bw.size[1])):
	gauss_totals = 0
	# For each neighboring pixel
	for(u, v) in itertools.product(range(-3*sigma + x,3*sigma+1+x),range(-3*sigma + y,3*sigma+1+y)):
		if(u < 0 or v < 0 or u >= width or v >= height):
			continue
		gauss_totals += gaussian(x-u,y-v,sigma)
		convolution[x][y] += (bw_pix[u,v]) * gaussian(x-u,y-v,sigma)
	
	convolution[x][y] /= gauss_totals

	# sanity check
	#if convolution[x][y] > 1:
	#	raise Exception("Problem!")

smoothed = Image.new(bw.mode, bw.size)
smoothed_pix = smoothed.load()
for x, xval in enumerate(convolution):
	for y, yval in enumerate(convolution[x]):
		smoothed_pix[x,y] = int(convolution[x][y])
smoothed.save(name + "_smoothed.png")

gradient_threshold = 20

neighbor_offsets = [(-1,-1), (-1,0), (-1, 1), (0,1), (0, -1), (1,0), (1,1), (1,-1)]

gradients = [ [0 for col in range(bw.size[1])] for row in range(bw.size[0])]

# Loop over every pixel in the image and calculate the largest gradient
for (x,y) in itertools.product(range(bw.size[0]), range(bw.size[1])):
	pixel = convolution[x][y]
	# For each immediately neighboring pixel
	for (uidx, vidx) in neighbor_offsets:
		u = x + uidx
		v = y + vidx
		if u < 0 or y < 0 or u >= width or v >= height:
			continue
		gradient = abs(convolution[u][v] - pixel)
		if gradient > gradients[x][y]:
			gradients[x][y] = gradient

# Draw the edges
edges = bw.point(lambda i: 255)
edges_pix = edges.load()

# Loop over every pixel in the image and determine if it's an edge pixel
for (x,y) in itertools.product(range(bw.size[0]), range(bw.size[1])):
	gradient = gradients[x][y]
	# the gradient must be greater than some threshold set by the user
	if gradient < gradient_threshold:
		continue
	is_max = True
	# determine if the gradient is a local maximum
	for (uidx, vidx) in neighbor_offsets:
		u = x + uidx
		v = y + vidx
		if u < 0 or y < 0 or u >= width or v >= height:
			continue
		if gradients[u][v] > pixel:
			is_max = False
			break
	if is_max:
		edges_pix[x,y] = 0

edges.save(name + "_edges.png", "PNG")

