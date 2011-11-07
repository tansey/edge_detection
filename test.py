import Image
import math
import itertools

def gaussian(x, y, sigma):
	return (1 / (2*math.pi*sigma**2))*math.exp(-(x**2+y**2)/(2*sigma**2))

im = Image.open("stapler.png")
print im.format, im.size, im.mode
bw = im.convert("L")
bw.save("bw_stapler.png", "PNG")
bw_pix = bw.load()
width = bw.size[0]
height = bw.size[1]

sigma = 1
convolution = [ [0 for col in range(bw.size[1])] for row in range(bw.size[0])]
# Loop over every pixel in the image and apply the Gaussian filter
for (x,y) in itertools.product(range(bw.size[0]), range(bw.size[1])):
	# For each neighboring pixel
	for(u, v) in itertools.product(range(-3*sigma + x,3*sigma+1+x),range(-3*sigma + y,3*sigma+1+y)):
		if(u < 0 or v < 0 or u >= width or v >= height):
			continue
		convolution[x][y] += (bw_pix[u,v] / 255) * gaussian(x-u,y-v,sigma)
	#print x, y, convolution[x][y]

	# sanity check
	if convolution[x][y] > 1:
		raise Exception("Problem!")

gradient_threshold = 0.1

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

"""
for x, x_vals in enumerate(convolution):
	for y, y_vals in enumerate(convolution[x]):
		edges_pix[x,y] = int(convolution[x][y] * 255)
"""

edges.save("edges.png", "PNG")

