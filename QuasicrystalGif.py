"""
The algorithm of codes of the file is copy from
	https://github.com/makeyourownmaker/QuasicrystalGifs/tree/main
I rewrite the code as my random graph tool.
"""

import numpy as np
from math import pi
from math import sqrt
from math import ceil
from matplotlib.colors import LightSource
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
import random
import matplotlib
import json
import matplotlib.image as mpimg

def RandBool():
	if random.randint(0,1) == 0:
		return True
	else:
		return False

def GetStdLineArray(gridX,gridY,waves,freq,offset=0,custom_waves=None):
	allwaves=(np.arange(0,pi,pi/waves)+offset/waves) if custom_waves is None else custom_waves
	xcos=gridX*np.cos(allwaves)[:,np.newaxis,np.newaxis]
	ysin=gridY*np.sin(allwaves)[:,np.newaxis,np.newaxis]
	ret=(xcos+ysin)*freq;
	return ret

def GetPolarLineArray(gridX,gridY,waves,freq,offset=0,custom_waves=None,sq=True,log=True):
	allwaves=(np.arange(0,pi,pi/waves)+offset/waves) if custom_waves is None else custom_waves
	theta=np.arctan2(gridX, gridY)
	r=gridX*gridX+gridY*gridY
	if sq: r=np.sqrt(r)
	if log: r=np.log(r)
	r[np.isinf(r) is True] = 0
	tcos=theta*np.cos(allwaves)[:,np.newaxis,np.newaxis]
	rsin=r*np.sin(allwaves)[:, np.newaxis, np.newaxis]
	ret=(tcos+rsin)*freq;
	return ret

def GeneratePolarFunc(sq,log):
	def retFunc(gridX,gridY,waves,freq,offset=0,custom_waves=None):
		return GetPolarLineArray(gridX,gridY,waves,freq,offset,custom_waves,sq,log)
	return retFunc

def GenerateQuasiCrystalPhase(waves,freq,width,height,scale=1,offset=0,jump_zero=False,custom_waves=None,func=GetStdLineArray):
	r=pi*scale
	if jump_zero:
		dx = np.arange(-r+r/width, r+r/width, 2*r/width,dtype=np.float64)
		dy = np.arange(-r+r/height, r+r/height, 2*r/height,dtype=np.float64)
	else:
		dx = np.arange(-r, r, 2*r/width,dtype=np.float64)
		dy = np.arange(-r, r, 2*r/height,dtype=np.float64)
	xv, yv = np.meshgrid(dx, dy)
	return func(xv,yv,waves,freq,offset,custom_waves)

#	bdmode=['hsv','overlay','soft']
#	cmap=['Accent', 'Blues', 'BrBG', 'BuGn',		'BuPu', 'CMRmap', 'Dark2', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PRGn', 'Paired',
#			 'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy', 'RdPu', 'RdYlBu', 'RdYlGn', 'Reds',
#			 'Set1', 'Set2', 'Set3', 'Spectral', 'Wistia', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'afmhot', 'autumn', 'binary', 'bone', 'brg',
#			 'bwr', 'cividis', 'cool', 'coolwarm', 'copper', 'cubehelix', 'flag', 'gist_earth', 'gist_gray', 'gist_heat', 'gist_ncar',
#			 'gist_rainbow', 'gist_stern', 'gist_yarg', 'gnuplot', 'gnuplot2', 'gray', 'hot', 'hsv', 'inferno', 'jet', 'magma', 'nipy_spectral',
#			 'ocean', 'pink', 'plasma', 'prism', 'rainbow', 'seismic', 'spring', 'summer', 'tab10', 'tab20', 'tab20b', 'tab20c', 'terrain',
#			 'turbo', 'twilight', 'twilight_shifted', 'viridis', 'winter']
# or add _r, like 'gray_r'

def GenerateImageProducer(blend_mode,azdeg,altdeg,vexag):
	AllBlendMode=['hsv','overlay','soft']
	func=None
	if blend_mode not in AllBlendMode:
		def func(image,cmap):
			return image
	else:
		ls = LightSource(azdeg=azdeg, altdeg=altdeg)
		def func(image,cmap):
			return ls.shade(image,cmap=plt.get_cmap(cmap),blend_mode=blend_mode,vert_exag=vexag)
	return func

def GenerateQuasiCrystalImage(data,image,cmap,imageFunc,calcFunc=None):
	if calcFunc is None: calcFunc = lambda data : np.cos(data)
	if imageFunc is None: imageFunc = GenerateImageProducer(None,0,0,0)
	image[:] = np.sum(calcFunc(data), axis=0)
	rgb = imageFunc(image,cmap)
	im = plt.imshow(rgb,cmap=cmap)
	return im

def ShowQuasiCrystalImage(data,image,cmap,blend_mode='None',azdeg=250,altdeg=50,vexag=1,calcFunc=None):
	imageFunc = GenerateImageProducer(blend_mode,azdeg,altdeg,vexag)
	return GenerateQuasiCrystalImage(data,image,cmap,imageFunc)

def ShowQuasiCrystalAnimate(data,image,figure,frames,delay,cmap,blend_mode='None',azdeg=250,altdeg=50,vexag=1,calcFunc=None,path=None):
	if calcFunc is None: calcFunc = lambda data : np.cos(data)
	phases = np.arange(0,2*pi,2*pi/frames)
	imageFunc = GenerateImageProducer(blend_mode,azdeg,altdeg,vexag)

	def animate_func(i):
		adata=data+phases[i]
		im = GenerateQuasiCrystalImage(adata,image,cmap,imageFunc,calcFunc)
		return [im]

	ani = animation.FuncAnimation(figure,animate_func,frames=frames,interval=delay)
	if path is not None:
		ani.save(path,writer='pillow')
	return ani;

def CalcQuasiCrystalAnimate(width,height,scale_array,waves_array,freq_array,offset_array,phase_array,image,figure,frames,delay,cmap,func,jump_zero=False,blend_mode='None',azdeg=250,altdeg=50,vexag=1,calcFunc=None,path=None):
	if calcFunc is None: calcFunc = lambda data : np.cos(data)
	imageFunc = GenerateImageProducer(blend_mode,azdeg,altdeg,vexag)

	ls=len(scale_array)
	lw=len(waves_array)
	lf=len(freq_array)
	lo=len(offset_array)
	lp=len(phase_array)

	def animate_func(i):
		data=GenerateQuasiCrystalPhase(waves_array[i%lw],freq_array[i%lf],width,height,scale_array[i%ls],offset_array[i%lo],jump_zero,custom_waves=None,func=func)
		adata=data+phase_array[i%lp]
		im = GenerateQuasiCrystalImage(adata,image,cmap,imageFunc,calcFunc)
		return [im]

	ani = animation.FuncAnimation(figure,animate_func,frames=frames,interval=delay)
	if path is not None:
		ani.save(path,writer='pillow')
	return ani

#管理參數的類別。如果要取得的參數沒有設定，根據不同的取得成員函式產生亂數給呼叫者。
class ParamSaver:
	def __init__(self):
		self.params={}

	def output(self):
		return json.dumps(self.params,indent=4)

	def load(self, json_string):
		self.params=json.loads(json_string)

	def set(self, key, value):
		if value is not None:
			self.params[key]=value

	def get(self, key):
		try:
			return self.params[key]
		except:
			return None

	def getBool(self, key):
		v=self.get(key)
		if v is None:
			return RandBool()
		else:
			return v

	def getInt(self, key, min, max=None):
		v=self.get(key)
		if v is None:
			if max==None:
				return min
			else:
				return random.randint(min,max)
		else:
			return int(v)

	def getString(self,key,default):
		v=self.get(key)
		if v is None:
			return default
		else:
			return v

	def getFloat(self, key, min, max=None):
		v=self.get(key)
		if v is None:
			if max==None:
				return min
			else:
				return random.random() * (max - min) + min
		else:
			return float(v)

	def getChoice(self, key, choices, toChoice=True):
		v=self.get(key)
		if v is None and toChoice:
			return random.choice(choices)
		else:
			return v

	def getNumericArray(self, key, min, maxStep, length, periodic=False):
		v=self.get(key)
		if v is list:
			return v;
		if maxStep==0 or length <= 0 or RandBool():
			return [min]
		if type(maxStep)==int:
			step=random.randint(1,maxStep) if maxStep > 0 else random.randint(-maxStep,0)
		else:
			step=maxStep
		if periodic==False:
			return [min+i*step for i in range(0,length)]
		if length%2==0:
			half_ret = [min+i*step for i in range(0,int(length/2)+1)]
			return half_ret+half_ret[::-1][1:-1]
		else:
			helf_ret = [min+i*step for i in range(0,int(length/2)+1)]
			return helf_ret+helf_ret[::-1][:-1]

	def hasNumericArray(self, key):
		v=self.get(key)
		return v is list

	def generateInfoString(self):
		w=self.getInt("waves",0,)
		f=self.getInt("freq",0,)
		m=self.getString("calcFunc","None")
		cmap=self.getString("colormap","None")
		if m=="polar" or m=="logpolar":
			s=self.getInt("scale",0)
			return "waves_%d_freq_%d_%s%d_colormap_%s" % (w,f,m,s,cmap)
		else:
			return "waves_%d_freq_%d_colormap_%s" % (w,f,cmap)

	def save(self, path):
		v=self.output()
		try:
			with open(path, 'w', encoding='utf-8') as f:
				f.write(v)
			print("write success: " + path)
		except IOError as e:
			print("write fail: " + e)

	def loadFile(self, path):
		try:
			with open(path, 'r', encoding='utf-8') as f:
				self.load(f.read())
			print("read success: " + path)
		except IOError as e:
			print("read fail: " + e)


