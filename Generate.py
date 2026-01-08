import sys
import os
import math
import random
import numpy as np
from QuasicrystalGif import * 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import argparse


# 基礎隨機布林函數
def RandBool():
	if random.randint(0,1) == 0:
		return True
	else:
		return False

# 所有可用的 Matplotlib Colormaps (色表)
AllCmp = ['Accent', 'Blues', 'BrBG', 'BuGn',  'BuPu',  'CMRmap', 'Dark2', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PRGn', 'Paired',
		  'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy', 'RdPu', 'RdYlBu', 'RdYlGn', 'Reds',
		  'Set1', 'Set2', 'Set3', 'Spectral', 'Wistia', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'afmhot', 'autumn', 'binary', 'bone', 'brg',
		  'bwr', 'cividis', 'cool', 'coolwarm', 'copper', 'cubehelix', 'flag', 'gist_earth', 'gist_gray', 'gist_heat', 'gist_ncar',
		  'gist_rainbow', 'gist_stern', 'gist_yarg', 'gnuplot', 'gnuplot2', 'gray', 'hot', 'hsv', 'inferno', 'jet', 'magma', 'nipy_spectral',
		  'ocean', 'pink', 'plasma', 'prism', 'rainbow', 'seismic', 'spring', 'summer', 'tab10', 'tab20', 'tab20b', 'tab20c', 'terrain',
		  'turbo', 'twilight', 'twilight_shifted', 'viridis', 'winter']


def main(input,args):
    # 如果輸出的資料夾不存在則建立
	if not os.path.isdir(args.folder):
		os.mkdir(args.folder)

	num=1 if args.num is None else args.num

    # 開始批次產生圖案
	for k in range(num):
		output=ParamSaver()         # 建立一個新的參數紀錄器，準備儲存這一次生成的設定
		name = '{0:05}'.format(k+1) # 檔案編號 (例如 00001)
		print('start:'+name)

        # 從 input (可能是外部讀入或隨機) 取得各項幾何參數
		width = input.getInt("width",512)
		height = input.getInt("height",512)
		scale=input.getInt("scale",1,input.getInt("maxScale",10))
		waves = input.getInt("waves",4,input.getInt("maxWaves",128))
		freq = input.getInt("freq",2,input.getInt("maxFreq",64))
		offset = input.getFloat("offset",0,pi if RandBool() else None)
		jump_zero = input.getBool("jump_zero")
        # 選擇座標轉換模式
		AllFunc=['default','polar','sqrtpolar','logpolar','sqrtlogpolar']
		calcFuncName=input.getChoice("calcFunc",AllFunc)
		if calcFuncName=='polar':
			func = GeneratePolarFunc(False,False)
		elif calcFuncName=='logpolar':
			func = GeneratePolarFunc(False,True)
		elif calcFuncName=='sqrtpolar':
			func = GeneratePolarFunc(True,False)
		elif calcFuncName=='sqrtlogpolar':
			func = GeneratePolarFunc(True,True)
		else:
			func = GetStdLineArray

        # 將選定的幾何參數存入 output 字典中
		output.set("width",width)
		output.set("height",height)
		output.set("scale",scale)
		output.set("waves",waves)
		output.set("freq",freq)
		output.set("offset",offset)
		output.set("jump_zero",jump_zero)
		output.set("calcFunc",calcFuncName)

        # 設定視覺與光照效果
		cmap = input.getChoice("colormap",plt.colormaps())
		AllBlendModes = ['hsv','overlay','soft']
		blend_mode=input.getChoice("blend_mode",AllBlendModes,RandBool())

		if blend_mode in AllBlendModes:
			azdeg=input.getInt("azdeg",0,360)
			altdeg=input.getInt("altdeg",0,90)
			vexag=input.getInt("vexag",1,10)
		else:
			azdeg=None
			altdeg=None
			vexag=None

		output.set("colormap",cmap)
		if blend_mode in AllBlendModes:
			output.set("blend_mode",blend_mode)
			if azdeg is not None:
				output.set("azdeg",azdeg)
			if altdeg is not None:
				output.set("altdeg",altdeg)
			if vexag is not None:
				output.set("vexag",vexag)
		else:
			output.set("blend_mode","None")

        # 1. 產生並儲存靜態圖片
		data = GenerateQuasiCrystalPhase(waves,freq,width,height,scale,offset,jump_zero,func=func)
		image = np.empty((height, width))
		fig = plt.figure(figsize=(width/100, height/100))
		ax = fig.add_axes([0, 0, 1, 1])
		ax.axis('off')

		fname=args.folder+'/'+name+output.generateInfoString()
		im=ShowQuasiCrystalImage(data,image,cmap,blend_mode,azdeg,altdeg,vexag)
		#mpimg.imsave(fname+'.png',image,cmap=cmap)
		im.write_png(fname+'.png')

        # 2. 產生並儲存基礎動畫 (僅相位改變)
		frames=input.getInt("frames",30)
		delay=input.getInt("delay",8)

		image = np.empty((height, width))
		fig = plt.figure(figsize=(width/100, height/100))
		ax = fig.add_axes([0, 0, 1, 1])
		ax.axis('off')
		ShowQuasiCrystalAnimate(data,image,fig,frames,delay,cmap,blend_mode,azdeg,altdeg,vexag,path=fname+'.gif')

        # 3. 產生進階動畫 (波數、頻率、縮放隨時間變動)
		frames=input.getInt("frames",16,input.getInt("max_frames",32))
		offset_array=input.getNumericArray("offset_array",offset,offset,frames,RandBool())
		phase_array=input.getNumericArray("phase_array",0,2*pi/frames,frames)
		waves_array=input.getNumericArray("waves_array",waves,input.getInt("max_waves_step",4),frames,RandBool())
		freq_array=input.getNumericArray("freq_array",freq,input.getInt("max_freq_step",6),frames,RandBool())
		scale_array=input.getNumericArray("scale_array",scale,input.getInt("max_scale_step",ceil(scale*0.1)),frames,RandBool())

        # 確保進階動畫中至少有一個參數是會變動的，否則重新生成陣列
		testTrival=not(input.hasNumericArray("waves_array") and input.hasNumericArray("freq_array") and input.hasNumericArray("scale_array"))
		while testTrival:
			if len(waves_array)>1 or len(freq_array)>1 or len(scale_array)>1:
				break
			waves_array=input.getNumericArray("waves_array",waves,input.getInt("max_waves_step",4),frames,RandBool())
			freq_array=input.getNumericArray("freq_array",freq,input.getInt("max_freq_step",6),frames,RandBool())
			scale_array=input.getNumericArray("scale_array",scale,input.getInt("max_scale_step",ceil(scale*0.1)),frames,RandBool())

        # 儲存完整的動畫參數至 JSON
		output.set("frames",frames)
		output.set("delay",delay)
		output.set("waves_array",waves_array)
		output.set("freq_array",freq_array)
		output.set("offset_array",offset_array)
		output.set("phase_array",phase_array)
		output.set("scale_array",scale_array)
		output.save(fname+'.json')

        # 4. 計算並儲存進階動畫影片 (_v.gif)
		image = np.empty((height, width))
		fig = plt.figure(figsize=(width/100, height/100))
		ax = fig.add_axes([0, 0, 1, 1])
		ax.axis('off')
		ani=CalcQuasiCrystalAnimate(width,height,scale_array,waves_array,freq_array,offset_array,phase_array,image,fig,frames,100,cmap,func,jump_zero,blend_mode,azdeg,altdeg,vexag,path=fname+'_v.gif')


# 命令列參數解析與環境設定
if __name__ == '__main__':
	def float_range(min_value, max_value):
		# 輔助：檢查浮點數範圍
		def range_checker(value):
			fvalue = float(value)
			if fvalue < min_value or fvalue > max_value:
				raise argparse.ArgumentTypeError(
					f"invalid float value: {value} is not within the range [{min_value}, {max_value}]"
				)
			return fvalue
		return range_checker

	parser = argparse.ArgumentParser(
			description="Generate animated gifs of quasicrystals using sum of plane waves. Copy and modified from\n https://github.com/makeyourownmaker/QuasicrystalGifs")

    # 設定必填參數
	required = parser.add_argument_group('required arguments')
	required.add_argument('-fd', '--folder', help='Foder for files for animation', type=str, required=True)

    # 設定選填參數 (包含各種隨機化與範圍限制)
	optional = parser._action_groups.pop()
	optional.add_argument('-n', '--num', help='Number of images - default=%(default)s', default=1, type=int)
	optional.add_argument('-rs', '--resolution', help='Image size in pixels', type=int, metavar="[64, 4096]", choices=range(64, 4096))
	optional.add_argument('-sl', '--scale', help='Scale for image range', type=int, choices=range(1,10000))
	optional.add_argument('-msl', '--max_scale', help='Max scale for image range', type=int, choices=range(1,10000))
	optional.add_argument('-wa', '--waves', help='Number of plane waves', type=int, metavar="[4, 550]", choices=range(4, 551))
	optional.add_argument('-mwa', '--max_waves', help='Max number of plane waves (in random)', type=int, metavar="[4, 550]", choices=range(4, 551))
	optional.add_argument('-ft', '--frequencies', help='Frequencies of each wave', type=int, metavar="[2, 550]", choices=range(2, 551))
	optional.add_argument('-mft', '--max_frequencies', help='Max frequencies of each wave (in random)', type=int, metavar="[2, 550]", choices=range(2, 551))
	optional.add_argument('-of', '--offset', help='Offset of each wave', type=float, metavar="[0, 2*pi]", choices=float_range(0, 2*math.pi))
	optional.add_argument('-jz', '--jump_zero', help='Jump zero near center', type=bool)
	optional.add_argument('-mt', '--method', help='Method of axis transformation', choices=['default','polar','sqrtpolar','logpolar','sqrtlogpolar'])
	optional.add_argument('-it', '--iterations', help='Number of frames in animation', type=int, metavar="[1, 120]", choices=range(1, 120))
	optional.add_argument('-de', '--delay', help='Number of microseconds between animation frames', type=int, metavar="[1, 100]", choices=range(1, 100))
	optional.add_argument('-cm', '--colormap', help='Matplotlib colormap See https://bit.ly/2WyFI4f', type=str, choices=plt.colormaps())

	optional.add_argument('-bm', '--blend_mode', help="Blend mode for light source. For most topographic surfaces, 'overlay' or 'soft' appear more visually realistic.", type=str, choices=['hsv', 'overlay', 'soft','None'])
	optional.add_argument('-az', '--azimuth', help='Azimuth for light source measured clockwise from north in degrees', type=int, metavar="[0, 360]", choices=range(0, 361))
	optional.add_argument('-el', '--elevation', help='Elevation for light source measured up from zero plane of the surface in degrees', type=int, metavar="[0, 90]", choices=range(0, 91))
	optional.add_argument('-ve', '--vert_exag', help='Amount to exaggerate or de-emphasize elevation values by when calculating light source illumination', type=int, metavar="[0, 10]", choices=range(1, 11))
	# NOTE vertical exaggeration of 10 is an arbitrary upper bound
	optional.add_argument('-mit', '--maxIterations', help='Max number of frames in animation', type=int, metavar="[1, 120]", choices=range(1, 180))
	optional.add_argument('-msls', '--max_scale_step', help='Max scale step for image range', type=int, choices=range(1,100))
	optional.add_argument('-mwas', '--max_waves_step', help='Max number of plane waves step', type=int, metavar="[1, 100]", choices=range(1, 101))
	optional.add_argument('-mfts', '--max_frequencies_step', help='Max frequencies step of each wave', type=int, metavar="[1, 100]", choices=range(1, 101))
	optional.add_argument('-in', '--input', help='Input file path for default settings.', default='Produce3.json')

	optional.add_argument('-q', '--quiet', help='Turn off messages - default=%(default)s', default=False, action='store_true')

	parser._action_groups.append(optional)
	args = parser.parse_args()

    # 初始化 ParamSaver 並嘗試讀取外部設定檔
	input=ParamSaver()
	try:
		input.loadFile(args.input)
	except:
		input=ParamSaver()      # 讀取失敗則使用全空白設定(全亂數)

    # 將命令行輸入的參數強制覆蓋進 input_saver
	input.set("width",args.resolution)
	input.set("height",args.resolution)
	input.set("scale",args.scale)
	input.set("maxScale",args.max_scale)
	input.set("waves",args.waves)
	input.set("maxWaves",args.max_waves)
	input.set("freq",args.frequencies)
	input.set("maxFreq",args.max_frequencies)
	input.set("offset",args.offset)
	input.set("jump_zero",args.jump_zero)
	input.set("calcFunc",args.method)
	input.set("colormap",args.colormap)
	input.set("blend_mode",args.blend_mode)
	input.set("azdeg",args.azimuth)
	input.set("altdeg",args.elevation)
	input.set("vexag",args.vert_exag)
	input.set("frames",args.iterations)
	input.set("delay",args.delay)
	input.set("max_frames",args.maxIterations)
	input.set("max_scale_step",args.max_scale_step)
	input.set("max_waves_step",args.max_waves_step)
	input.set("max_freq_step",args.max_frequencies_step)

	main(input,args)
