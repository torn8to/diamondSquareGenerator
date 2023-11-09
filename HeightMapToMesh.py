import matplotlib.pyplot as plt
import numpy as np
from diamondSquareAlgorithim import diamondSquareGenerator, periodic
from plyfile import PlyData, PlyElement
from perlin_numpy import(generate_perlin_noise_2d)
COLORS = {
	"grass": (34, 139, 34),
	"forest": (0, 100, 0),
	"rock": (139, 137, 137),
	"snow": (255, 250, 250),
	"sand": (238, 214, 175),
	"water": (65, 105, 255),
}


def scaleHeightMap(arr: np.ndarray) -> np.ndarray:
	min = np.min(arr)
	max = np.max(arr)
	arr = arr + np.abs(min)
	range = max - min
	return arr / range


def generateSlopeMap(arr: np.ndarray) -> np.ndarray:
	return np.gradient(arr)[0]


def getColor(height: float, slope: float) -> tuple:
	if height > .7:
		return COLORS["snow"]
	elif height > .5 and slope > .001:
		return COLORS["rock"]
	elif height > .10:
		return COLORS["forest"]
	elif height > .05:
		return COLORS["grass"]
	elif height > .03:
		return COLORS['sand']
	else:
		return COLORS['water']





def getColoredMap(heightMap,slopeMap):
	heightMapShape = heightMap.shape
	slopeMap = np.abs(slopeMap)
	coloredMap = np.zeros((heightMapShape[0],heightMapShape[1],3))
	for x in range(heightMapShape[0]-1):
		for y in range(heightMapShape[1]-1):
			coloredMap[x][y] = getColor(heightMap[x][y], slopeMap[x][y])
	return coloredMap.astype(np.uint8)


def generateVertices(heightMap):
	shape = heightMap.shape
	vertices = []
	base = (-1, -0.75, -1)
	size = 2
	max_height = 0.5
	step_x = size / (shape[0] - 1)
	step_y = size / (shape[1] - 1)
	
	for x in range(shape[0]):
		for y in range(shape[1]):
			x_coord = base[0] + step_x * x
			y_coord = base[1] + max_height * heightMap[x][y]
			z_coord = base[2] + step_y * y
			vertices.append((x_coord, y_coord, z_coord))
	print("Vertices generated")
	vertices = np.array(vertices,dtype=[('x', 'f4'), ('y', 'f4',), ('z', 'f4')])
	return vertices


def generateColoredVertices(heightMap, colorMap):
	shape = heightMap.shape
	vertices = []
	base = (-1, -0.75, -1)
	size = 2
	max_height = 0.5
	step_x = size / (shape[0] - 1)
	step_y = size / (shape[1] - 1)
	
	for x in range(shape[0]):
		for y in range(shape[1]):
			x_coord = base[0] + step_x * x
			y_coord = base[1] + max_height * heightMap[x][y]
			z_coord = base[2] + step_y * y
			colors = colorMap[x][y]
			vertices.append((x_coord, y_coord, z_coord, colors[0], colors[1], colors[2]))
	vertices = np.array(vertices, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')])
	print("Vertices generated")
	return vertices


def generateFaces(heightMap):
	edges = []
	surfaces = []
	shape = heightMap.shape
	
	for x in range(shape[0] - 1):
		for y in range(shape[1] - 1):
			base = x * shape[0] + y
			a = base
			b = base + 1
			c = base + shape[0] + 1
			d = base + shape[0]
			edges.append((a, b))
			edges.append((b, c))
			edges.append((c, a))
			edges.append((c, d))
			edges.append((d, a))
			surfaces.append([a, b, c])
			surfaces.append([a, c, d])
	print("Edges, surfaces generated")
	faces_array = np.empty(len(surfaces), dtype=[('vertex_indices', 'i4', (3,))])
	faces_array['vertex_indices'] = surfaces
	return edges, faces_array

def generateColoredFaces(heightMap,coloredMap):
	edges = []
	surfaces = []
	shape = heightMap.shape
	for x in range(shape[0] - 1):
		for y in range(shape[1] - 1):
			base = x * shape[0] + y
			a = base
			b = base + 1
			c = base + shape[0] + 1
			d = base + shape[0]
			edges.append((a, b))
			edges.append((b, c))
			edges.append((c, a))
			edges.append((c, d))
			edges.append((d, a))
			colors = coloredMap[x,y]
			surfaces.append(((a, b, c),colors[0],colors[1],colors[2]))
			surfaces.append(((a, c, d),colors[0],colors[1],colors[2]))
	print("Edges, surfaces generated")
	surfaces = np.array(surfaces,dtype=[('vertex_indices', 'i4', (3,)), ('red', 'u1'), ('green', 'u1'),('blue', 'u1')])
	return edges, surfaces
	


def saveToOBJ(vertices: np.ndarray, triangles: np.ndarray, colors:np.ndarray or None = None,  filename = "model.obj"):
	file = open(filename, "w")
	if type(colors) is np.ndarray:
		colors = np.reshape(colors, (-1, 3))
		assert len(vertices) == len(colors)
		for vertex, color in zip(vertices, colors):
			file.write("v " + str(vertex[0]) + " " + str(vertex[1]) + " " + str(vertex[2]) + " " + str(color[0] / 255) + " " + str(	color[1] / 255) + str(color[2] / 255) + "\n")
	else:
		for vertex, color in zip(vertices, colors):
			file.write("v " + str(vertex[0]) + " " + str(vertex[1]) + " " + str(vertex[2]) + "\n")
	for tri in triangles:
		file.write("f " + str(tri[2] + 1) + " " + str(tri[1] + 1) + " " + str(tri[0] + 1) + "\n")
	file.close()
	print(filename, "saved")
	
	
def saveToPLY(vertices:np.ndarray,surface_list:np.ndarray,filename="model.ply"):
	file = open(filename, "wb")
	verts = PlyElement.describe(vertices,'vertex')
	faces = PlyElement.describe(surface_list, 'face')
	data = PlyData([verts,faces], text=True).write(file)
	
			
def heightMapToPly(heightMap):
	height_map = heightMap ** 2
	scaled_map = scaleHeightMap(height_map)
	slope_map = generateSlopeMap(scaled_map)
	colored_map = getColoredMap(scaled_map,slope_map)
	verts = generateColoredVertices(height_map,colored_map)
	edges, surfaces = generateFaces(height_map)
	saveToPLY(verts,surfaces)



def generate2dPerlinWormsBinary(size ):
	noise = generate_perlin_noise_2d((size, size), (1, 1))
	base:np.ndarray = .15>np.abs(noise)
	worms = base.astype(np.int8)
	return worms


def generateSquareHeightMapToPly(size = 512):
	height_map = generate_perlin_noise_2d((size, size), (4, 4))
	scaled_map = scaleHeightMap(height_map)
	slope_map = generateSlopeMap(scaled_map)
	color_map = getColoredMap(height_map,slope_map)
	verts = generateColoredVertices(height_map,color_map)
	edges, faces = generateFaces(height_map)
	plt.imshow(color_map)
	plt.show()




generateSquareHeightMapToPly(512)


	



'''
height_map = diamondSquareGenerator(2**9+1,.5, periodic)
height_map = height_map ** 2
scaled_map = scaleHeightMap(height_map)
slope_map = generateSlopeMap(scaled_map)
#height_map = height_map[2:height_map.shape[0]-3,2:height_map.shape[1]-3]
#slope_map = slope_map[2:slope_map.shape[0]-3,2:slope_map.shape[1]-3]
heightMapToPly(height_map,getColoredMap(he))

'''


