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

# 輔助函數：隨機回傳 True 或 False
def RandBool():
	if random.randint(0,1) == 0:
		return True
	else:
		return False

# 產生標準的線性波陣列 (Standard Line Array)
# 透過在不同角度 (allwaves) 上產生的平面波疊加
def GetStdLineArray(gridX,gridY,waves,freq,offset=0,custom_waves=None):
    # 計算對應的波方向角度
	allwaves=(np.arange(0,pi,pi/waves)+offset/waves) if custom_waves is None else custom_waves
    # 利用投影公式 x*cos(theta) + y*sin(theta) 計算相位
	xcos=gridX*np.cos(allwaves)[:,np.newaxis,np.newaxis]
	ysin=gridY*np.sin(allwaves)[:,np.newaxis,np.newaxis]
	ret=(xcos+ysin)*freq;
	return ret

# 產生極座標波陣列 (Polar Line Array)
# 會產生旋轉對稱或圓環狀的干涉圖案
def GetPolarLineArray(gridX,gridY,waves,freq,offset=0,custom_waves=None,sq=True,log=True):
	allwaves=(np.arange(0,pi,pi/waves)+offset/waves) if custom_waves is None else custom_waves
	theta=np.arctan2(gridX, gridY)          # 計算角度
	r=gridX*gridX+gridY*gridY               # 計算距離平方
	if sq: r=np.sqrt(r)                     # 是否取平方根 (線性距離)
	if log: r=np.log(r)                     # 是否取對數 (產生向中心縮小的效果)
	r[np.isinf(r) is True] = 0              # 處理對數產生的無限大數值
    # 將角度相位與徑向相位結合
	tcos=theta*np.cos(allwaves)[:,np.newaxis,np.newaxis]
	rsin=r*np.sin(allwaves)[:, np.newaxis, np.newaxis]
	ret=(tcos+rsin)*freq;
	return ret

# 閉包函數：用來快速生成特定設定的極座標計算函數
def GeneratePolarFunc(sq,log):
	def retFunc(gridX,gridY,waves,freq,offset=0,custom_waves=None):
		return GetPolarLineArray(gridX,gridY,waves,freq,offset,custom_waves,sq,log)
	return retFunc

# 核心函數：產生準晶體的相位矩陣
# width/height: 圖片解析度, scale: 座標縮放, freq: 頻率(影響條紋密度)
def GenerateQuasiCrystalPhase(waves,freq,width,height,scale=1,offset=0,jump_zero=False,custom_waves=None,func=GetStdLineArray):
	r=pi*scale
    # 建立網格座標系統
	if jump_zero:
		dx = np.arange(-r+r/width, r+r/width, 2*r/width,dtype=np.float64)
		dy = np.arange(-r+r/height, r+r/height, 2*r/height,dtype=np.float64)
	else:
		dx = np.arange(-r, r, 2*r/width,dtype=np.float64)
		dy = np.arange(-r, r, 2*r/height,dtype=np.float64)
	xv, yv = np.meshgrid(dx, dy)
    # 根據指定的函數 (標準或極座標) 產生相位
	return func(xv,yv,waves,freq,offset,custom_waves)

#   影像生成器：處理光照與著色 (Shading)
#   blend_mode: 混合模式 ('hsv', 'overlay', 'soft'), azdeg/altdeg: 光源方位角與高度角
#   顏色來自 plt 配色給的選擇
#	cmap=['Accent', 'Blues', 'BrBG', 'BuGn',		'BuPu', 'CMRmap', 'Dark2', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PRGn', 'Paired',
#			 'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy', 'RdPu', 'RdYlBu', 'RdYlGn', 'Reds',
#			 'Set1', 'Set2', 'Set3', 'Spectral', 'Wistia', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'afmhot', 'autumn', 'binary', 'bone', 'brg',
#			 'bwr', 'cividis', 'cool', 'coolwarm', 'copper', 'cubehelix', 'flag', 'gist_earth', 'gist_gray', 'gist_heat', 'gist_ncar',
#			 'gist_rainbow', 'gist_stern', 'gist_yarg', 'gnuplot', 'gnuplot2', 'gray', 'hot', 'hsv', 'inferno', 'jet', 'magma', 'nipy_spectral',
#			 'ocean', 'pink', 'plasma', 'prism', 'rainbow', 'seismic', 'spring', 'summer', 'tab10', 'tab20', 'tab20b', 'tab20c', 'terrain',
#			 'turbo', 'twilight', 'twilight_shifted', 'viridis', 'winter']
#   or add _r, like 'gray_r'

def GenerateImageProducer(blend_mode,azdeg,altdeg,vexag):
	AllBlendMode=['hsv','overlay','soft']
	func=None
	if blend_mode not in AllBlendMode:
		def func(image,cmap):
			return image    # 若無混合模式則直接回傳原圖
	else:
		ls = LightSource(azdeg=azdeg, altdeg=altdeg)
		def func(image,cmap):
            # 使用 Matplotlib 的 LightSource 產生具有立體感的陰影效果
			return ls.shade(image,cmap=plt.get_cmap(cmap),blend_mode=blend_mode,vert_exag=vexag)
	return func

# 核心繪製函數：將相位數據轉換為 RGB 影像
def GenerateQuasiCrystalImage(data,image,cmap,imageFunc,calcFunc=None):
	if calcFunc is None: calcFunc = lambda data : np.cos(data)
	if imageFunc is None: imageFunc = GenerateImageProducer(None,0,0,0)
    # 將所有波疊加並取餘弦值 (準晶體公式核心)
	image[:] = np.sum(calcFunc(data), axis=0)
	rgb = imageFunc(image,cmap)
	im = plt.imshow(rgb,cmap=cmap)
	return im

# 顯示靜態準晶體圖片
def ShowQuasiCrystalImage(data,image,cmap,blend_mode='None',azdeg=250,altdeg=50,vexag=1,calcFunc=None):
	imageFunc = GenerateImageProducer(blend_mode,azdeg,altdeg,vexag)
	return GenerateQuasiCrystalImage(data,image,cmap,imageFunc)

# 產生準晶體動畫：改變相位
# frames: 總幀數, delay: 幀間隔時間
def ShowQuasiCrystalAnimate(data,image,figure,frames,delay,cmap,blend_mode='None',azdeg=250,altdeg=50,vexag=1,calcFunc=None,path=None):
	if calcFunc is None: calcFunc = lambda data : np.cos(data)
	phases = np.arange(0,2*pi,2*pi/frames)      # 一個完整的 2pi 週期動畫
	imageFunc = GenerateImageProducer(blend_mode,azdeg,altdeg,vexag)

	def animate_func(i):
		adata=data+phases[i]            # 隨時間改變相位
		im = GenerateQuasiCrystalImage(adata,image,cmap,imageFunc,calcFunc)
		return [im]

	ani = animation.FuncAnimation(figure,animate_func,frames=frames,interval=delay)
	if path is not None:
		ani.save(path,writer='pillow')
	return ani;

# 進階動畫函數：可動態改變縮放、波數量、頻率等參數
def CalcQuasiCrystalAnimate(width,height,scale_array,waves_array,freq_array,offset_array,phase_array,image,figure,frames,delay,cmap,func,jump_zero=False,blend_mode='None',azdeg=250,altdeg=50,vexag=1,calcFunc=None,path=None):
	if calcFunc is None: calcFunc = lambda data : np.cos(data)
	imageFunc = GenerateImageProducer(blend_mode,azdeg,altdeg,vexag)

    # 取得各參數數組長度，用於循環取值 (Modulo)
	ls=len(scale_array)
	lw=len(waves_array)
	lf=len(freq_array)
	lo=len(offset_array)
	lp=len(phase_array)

	def animate_func(i):
        # 每一幀都重新計算相位網格
		data=GenerateQuasiCrystalPhase(waves_array[i%lw],freq_array[i%lf],width,height,scale_array[i%ls],offset_array[i%lo],jump_zero,custom_waves=None,func=func)
		adata=data+phase_array[i%lp]
		im = GenerateQuasiCrystalImage(adata,image,cmap,imageFunc,calcFunc)
		return [im]

	ani = animation.FuncAnimation(figure,animate_func,frames=frames,interval=delay)
	if path is not None:
		ani.save(path,writer='pillow')
	return ani

# 管理參數的類別。
# 功能：
# 1. 紀錄部分參數（透過 JSON 格式）。
# 2. 如果要取得的參數沒有預設值，會根據資料型態自動產生亂數回傳，方便隨機藝術創作。
class ParamSaver:
	def __init__(self):
        # 存放參數的字典
		self.params={}

    # 將目前的參數轉換為格式化的 JSON 字串
	def output(self):
		return json.dumps(self.params,indent=4)

    # 從 JSON 字串載入參數
	def load(self, json_string):
		self.params=json.loads(json_string)

    # 設定參數，若 value 為空則不動作
	def set(self, key, value):
		if value is not None:
			self.params[key]=value

    # 基礎取得函式：若鍵值不存在則回傳 None
	def get(self, key):
		try:
			return self.params[key]
		except:
			return None

    # 取得布林值：若無設定則回傳隨機 True/False
	def getBool(self, key):
		v=self.get(key)
		if v is None:
			return RandBool()
		else:
			return v

    # 取得整數：若無設定，且有提供 max 則回傳範圍亂數，否則回傳 min 預設值
	def getInt(self, key, min, max=None):
		v=self.get(key)
		if v is None:
			if max==None:
				return min
			else:
				return random.randint(min,max)
		else:
			return int(v)

    # 取得字串：若無設定則回傳 default 預設值
	def getString(self,key,default):
		v=self.get(key)
		if v is None:
			return default
		else:
			return v

    # 取得浮點數：若無設定，則在 [min, max) 範圍內產生亂數
	def getFloat(self, key, min, max=None):
		v=self.get(key)
		if v is None:
			if max==None:
				return min
			else:
				return random.random() * (max - min) + min
		else:
			return float(v)

    # 從列表 (choices) 中挑選：若無設定且 toChoice 為真，則隨機選一個
	def getChoice(self, key, choices, toChoice=True):
		v=self.get(key)
		if v is None and toChoice:
			return random.choice(choices)
		else:
			return v

    # 取得數值陣列（用於動畫序列）：
	# 可以產生等差級數或週期性（鏡像對稱）的陣列
	def getNumericArray(self, key, min, maxStep, length, periodic=False):
		v=self.get(key)
		if v is list:
			return v;
        # 隨機決定是否不產生陣列，僅回傳包含單一值的清單
		if maxStep==0 or length <= 0 or RandBool():
			return [min]
        # 決定遞增/遞減步長
		if type(maxStep)==int:
			step=random.randint(1,maxStep) if maxStep > 0 else random.randint(-maxStep,0)
		else:
			step=maxStep
		if periodic==False:
            # 產生一般的等差數列
			return [min+i*step for i in range(0,length)]
        # 產生鏡像對稱的數列（例如 1,2,3,2,1），使動畫循環銜接順暢
		if length%2==0:
			half_ret = [min+i*step for i in range(0,int(length/2)+1)]
			return half_ret+half_ret[::-1][1:-1]
		else:
			helf_ret = [min+i*step for i in range(0,int(length/2)+1)]
			return helf_ret+helf_ret[::-1][:-1]

    # 判斷參數是否為陣列型態
	def hasNumericArray(self, key):
		v=self.get(key)
		return v is list

    # 生成描述字串：用於存檔時自動命名，包含波數、頻率、計算方式與色表資訊
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

    # 將目前的參數字典存入檔案 (JSON)
	def save(self, path):
		v=self.output()
		try:
			with open(path, 'w', encoding='utf-8') as f:
				f.write(v)
			print("write success: " + path)
		except IOError as e:
			print("write fail: " + str(e))

    # 從檔案載入參數
	def loadFile(self, path):
		try:
			with open(path, 'r', encoding='utf-8') as f:
				self.load(f.read())
			print("read success: " + path)
		except IOError as e:
			print("read fail: " + str(e))



